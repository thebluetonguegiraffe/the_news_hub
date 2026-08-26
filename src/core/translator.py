import logging
import random
import re
import time
from typing import List, Optional

import requests
from bs4 import BeautifulSoup


logger = logging.getLogger("translator")
logger.setLevel(logging.INFO)


class TranslationError(Exception):
    pass


class RateLimitError(TranslationError):
    """Google is throttling this IP. Retrying immediately will not help."""

    pass


class GoogleTranslator:
    BASE_URL = "https://translate.googleapis.com/translate_a/single"
    TRANSLATE_URL = "https://translate.google.com/m"

    # Google rejects requests over ~5000 chars. Stay well under it: the whole
    # batch travels in the query string, so the URL length counts too.
    MAX_BATCH_CHARS = 3500
    # Blocks last minutes, not seconds, so back off hard instead of hammering.
    MAX_RETRIES = 3
    BACKOFF_BASE_SECONDS = 10
    MIN_REQUEST_INTERVAL = 1.5

    USER_AGENT = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    def __init__(self, source_lang: str = None):
        """Initialize Google Translator with cache"""
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})
        self.source_lang = source_lang
        self._cache = {}
        self._last_request_at = 0.0

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

        return results

    def _translate_chunk(self, chunk, target_lang):
        """Translate one chunk, falling back to one-by-one if the batch fails."""
        texts = [text for _, text in chunk]
        try:
            translations = self._request("\n".join(texts), target_lang).split("\n")
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
                resolved.append((index, None))
                continue
            self._cache[(text, self.source_lang, target_lang)] = translated
            resolved.append((index, translated))
        return resolved

    def _translate_individually(self, chunk, target_lang):
        resolved = []
        for index, text in chunk:
            try:
                translated = self._request(text, target_lang).strip()
            except TranslationError as e:
                logger.warning(f"Could not translate {text[:60]!r}: {e}")
                resolved.append((index, None))
                continue
            except Exception:
                # translate_batch must never take the caller down: report the
                # item as untranslated and keep the traceback for debugging.
                logger.exception(f"Unexpected error translating {text[:60]!r}")
                resolved.append((index, None))
                continue
            if translated:
                self._cache[(text, self.source_lang, target_lang)] = translated
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
        params = {"tl": target_lang, "q": text}
        if self.source_lang:
            params["sl"] = self.source_lang

        for attempt in range(self.MAX_RETRIES):
            try:
                self._throttle()
                response = self.session.get(self.TRANSLATE_URL, params=params, timeout=30)

                if response.status_code == 429:
                    raise RateLimitError("HTTP 429")
                response.raise_for_status()

                return self._parse(response.text)

            except (RateLimitError, requests.exceptions.RequestException) as e:
                if attempt == self.MAX_RETRIES - 1:
                    raise TranslationError(f"Failed after {self.MAX_RETRIES} attempts: {e}")
                sleep_time = self.BACKOFF_BASE_SECONDS * (3**attempt) * random.uniform(0.8, 1.2)
                logger.info(f"Request failed ({e}). Waiting {sleep_time:.1f}s before retry...")
                time.sleep(sleep_time)

    def _parse(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div", {"class": "result-container"}) or soup.find(
            "div", {"class": "t0"}
        )
        if element is None:
            # Google answers a block with HTTP 200 and an abuse interstitial
            # instead of the result, so a missing container means throttling,
            # not a text that has no translation.
            raise RateLimitError("no result container in response (likely throttled)")
        return element.get_text("\n")

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


if __name__ == "__main__":
    translator = GoogleTranslator("en")

    print("=== Google Translator Demo ===\n")

    result = translator.translate("Hello, how are you?", target_lang="es")
    print(f"Translation: {result}")
