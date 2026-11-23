import logging
import random
import re
import time
from typing import Dict, List, Optional

import requests


logger = logging.getLogger("translator")
logger.setLevel(logging.INFO)


class TranslationError(Exception):
    pass


class RateLimitError(TranslationError):
    """Google is throttling this IP. Retrying immediately will not help."""

    pass


class GoogleTranslator:
    # The JSON endpoint, not the translate.google.com/m HTML page the scraper
    # used before: that host answers this server with a 302 to
    # google.com/sorry/index (HTTP 429), so every translation failed. This one
    # answers the same requests from the same IP normally, needs no API key,
    # and returns the translation as data instead of markup to scrape.
    BASE_URL = "https://translate.googleapis.com/translate_a/single"

    # Google rejects requests over ~5000 chars. Stay well under it: the whole
    # batch travels in the query string, so the URL length counts too.
    MAX_BATCH_CHARS = 3500

    # Blocks last minutes, not seconds, so back off hard instead of hammering.
    MAX_RETRIES = 5
    BACKOFF_BASE_SECONDS = 15
    BACKOFF_FACTOR = 2
    BACKOFF_CAP_SECONDS = 120
    MIN_REQUEST_INTERVAL = 1.0

    # Once the retries for a single request are exhausted, the IP is blocked
    # rather than unlucky. Further requests fail fast for this long instead of
    # sleeping through the backoff again and again: an ingestion run with many
    # batches used to spend hours waiting on an endpoint that kept refusing.
    BLOCK_COOLDOWN_SECONDS = 600

    USER_AGENT = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    def __init__(self, source_lang: str = None):
        """Initialize Google Translator with cache"""
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})
        self.source_lang = source_lang
        self._cache: Dict = {}
        self._last_request_at = 0.0
        self._blocked_until = 0.0
        self.stats = {"requests": 0, "translated": 0, "failed": 0, "skipped_while_blocked": 0}

    def translate(self, text: str, target_lang: str) -> str:
        """Translate a single string. Raises TranslationError on failure."""
        if not text:
            raise TranslationError("Text cannot be empty")

        translated = self.translate_batch([text], target_lang)[0]
        if translated is None:
            raise TranslationError(f"Failed to translate: {text[:80]}")
        return translated

    def translate_batch(self, texts: List[str], target_lang: str) -> List[Optional[str]]:
        """
        Translate many strings using as few requests as possible.

        Google's /m endpoint keeps a 1:1 line mapping for multi-line input, so a
        whole batch of headlines fits in a single request. Returns a list the
        same length as `texts`, with None where a text could not be translated.
        Never raises: callers decide what to do with the missing entries.
        """
        if not texts:
            return []

        # Newlines are the batch separator, so they must not survive in the input.
        flattened = [self._flatten(text) for text in texts]
        results: List[Optional[str]] = [None] * len(flattened)

        pending = []
        for index, text in enumerate(flattened):
            if not text:
                continue
            if self.source_lang == target_lang:
                results[index] = text
                continue
            cached = self._cache.get((text, self.source_lang, target_lang))
            if cached is not None:
                results[index] = cached
                continue
            pending.append((index, text))

        for chunk in self._chunks(pending):
            for index, translated in self._translate_chunk(chunk, target_lang):
                results[index] = translated

        missing = sum(1 for index, _ in pending if results[index] is None)
        if missing:
            logger.warning(
                f"{missing}/{len(pending)} texts could not be translated to "
                f"{target_lang} (blocked={self.is_blocked})"
            )
        return results

    @property
    def is_blocked(self) -> bool:
        return time.monotonic() < self._blocked_until

    def log_stats(self) -> None:
        """Report what the endpoint actually delivered, so silent gaps surface."""
        logger.info(f"translator stats: {self.stats}")

    def _translate_chunk(self, chunk, target_lang):
        """Translate one chunk, falling back to one-by-one only when that can help."""
        texts = [text for _, text in chunk]
        try:
            translations = self._request("\n".join(texts), target_lang).split("\n")
        except RateLimitError:
            # Splitting a throttled batch into N single requests multiplies the
            # load on an endpoint that is already refusing us and deepens the
            # block, so report the whole chunk as untranslated instead.
            logger.warning(f"Batch of {len(texts)} hit the rate limit; skipping the chunk.")
            self.stats["failed"] += len(texts)
            return [(index, None) for index, _ in chunk]
        except Exception as e:
            logger.warning(f"Batch of {len(texts)} failed ({e}); retrying one by one.")
            return self._translate_individually(chunk, target_lang)

        # A length mismatch means the lines no longer line up with the inputs.
        # Assigning them anyway would silently attach the wrong text to an
        # article, so fall back rather than guess.
        if len(translations) != len(texts):
            logger.warning(
                f"Batch line mismatch (sent {len(texts)}, got {len(translations)}); "
                "retrying one by one."
            )
            return self._translate_individually(chunk, target_lang)

        resolved = []
        for (index, text), translated in zip(chunk, translations):
            translated = translated.strip()
            if not translated:
                self.stats["failed"] += 1
                resolved.append((index, None))
                continue
            self._cache[(text, self.source_lang, target_lang)] = translated
            self.stats["translated"] += 1
            resolved.append((index, translated))
        return resolved

    def _translate_individually(self, chunk, target_lang):
        resolved = []
        for index, text in chunk:
            try:
                translated = self._request(text, target_lang).strip()
            except TranslationError as e:
                logger.warning(f"Could not translate {text[:60]!r}: {e}")
                self.stats["failed"] += 1
                resolved.append((index, None))
                continue
            except Exception:
                # translate_batch must never take the caller down: report the
                # item as untranslated and keep the traceback for debugging.
                logger.exception(f"Unexpected error translating {text[:60]!r}")
                self.stats["failed"] += 1
                resolved.append((index, None))
                continue
            if translated:
                self._cache[(text, self.source_lang, target_lang)] = translated
                self.stats["translated"] += 1
            else:
                self.stats["failed"] += 1
            resolved.append((index, translated or None))
        return resolved

    def _chunks(self, pending):
        """Group texts into request-sized batches."""
        chunk, size = [], 0
        for index, text in pending:
            # +1 for the newline separator.
            cost = len(text) + 1
            if chunk and size + cost > self.MAX_BATCH_CHARS:
                yield chunk
                chunk, size = [], 0
            chunk.append((index, text))
            size += cost
        if chunk:
            yield chunk

    def _request(self, text: str, target_lang: str) -> str:
        """Send one translation request, retrying with a long backoff if blocked."""
        if self.is_blocked:
            self.stats["skipped_while_blocked"] += 1
            raise RateLimitError(
                f"still in cooldown for {self._blocked_until - time.monotonic():.0f}s"
            )

        params = {
            "client": "gtx",
            "dt": "t",
            "sl": self.source_lang or "auto",
            "tl": target_lang,
            "q": text,
        }

        for attempt in range(self.MAX_RETRIES):
            try:
                self._throttle()
                self.stats["requests"] += 1
                response = self.session.get(self.BASE_URL, params=params, timeout=30)

                if response.status_code == 429:
                    raise RateLimitError("HTTP 429")
                response.raise_for_status()

                return self._parse(response)

            except (RateLimitError, requests.exceptions.RequestException) as e:
                if attempt == self.MAX_RETRIES - 1:
                    # Stop paying the backoff on every later batch of this run.
                    self._blocked_until = time.monotonic() + self.BLOCK_COOLDOWN_SECONDS
                    logger.warning(
                        f"Translation endpoint unavailable after {self.MAX_RETRIES} attempts; "
                        f"pausing translations for {self.BLOCK_COOLDOWN_SECONDS}s."
                    )
                    raise RateLimitError(f"Failed after {self.MAX_RETRIES} attempts: {e}")
                sleep_time = min(
                    self.BACKOFF_BASE_SECONDS * (self.BACKOFF_FACTOR**attempt),
                    self.BACKOFF_CAP_SECONDS,
                ) * random.uniform(0.8, 1.2)
                retry_after = self._retry_after(e)
                if retry_after:
                    sleep_time = max(sleep_time, retry_after)
                logger.info(f"Request failed ({e}). Waiting {sleep_time:.1f}s before retry...")
                time.sleep(sleep_time)

    @staticmethod
    def _retry_after(error: Exception) -> Optional[float]:
        """Respect an explicit Retry-After rather than guessing a backoff."""
        response = getattr(error, "response", None)
        if response is None:
            return None
        value = response.headers.get("Retry-After") if response.headers else None
        try:
            return float(value) if value else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse(response: requests.Response) -> str:
        """
        Pull the translated text out of the JSON payload.

        Google splits the input into sentence-sized segments and keeps the
        newlines inside them, so concatenating every segment rebuilds the
        submitted text line for line. That is what lets a whole batch travel in
        one request: the caller splits the result on newlines again and gets
        one translation per input line.
        """
        try:
            payload = response.json()
        except ValueError:
            # A block arrives as HTML (an abuse interstitial), not as JSON, so
            # unparseable content means throttling rather than an empty result.
            raise RateLimitError("response was not JSON (likely throttled)")

        try:
            segments = payload[0]
        except (IndexError, KeyError, TypeError):
            raise TranslationError(f"unexpected payload shape: {str(payload)[:120]}")

        if not segments:
            raise TranslationError("no translation in response")

        return "".join(
            segment[0] for segment in segments if segment and segment[0]
        )

    def _throttle(self):
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self.MIN_REQUEST_INTERVAL:
            time.sleep(self.MIN_REQUEST_INTERVAL - elapsed)
        self._last_request_at = time.monotonic()

    @staticmethod
    def _flatten(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip() if text else ""

    def detect_language(self, text: str) -> str:
        """Detect the language of the given text."""
        if not text or not text.strip():
            raise TranslationError("Text cannot be empty for language detection")

        params = {
            "client": "gtx",
            "sl": "auto",  # auto-detect source language
            "tl": "en",  # target doesn't matter for detection
            "dt": "t",
            "q": text.strip(),
        }

        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            detected_lang = data[2]
            return detected_lang

        except requests.exceptions.RequestException as e:
            raise TranslationError(f"Network error: {str(e)}")
        except (KeyError, IndexError, ValueError) as e:
            raise TranslationError(f"Failed to parse response: {str(e)}")
