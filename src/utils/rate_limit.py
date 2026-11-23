"""Shared retry/throttle helpers for the rate-limited Mistral API.

The chat endpoint on the current plan starts returning HTTP 429 after roughly
one request per second, so a burst of unguarded calls fails the whole run. Every
LLM call in the pipeline goes through `call_with_retry`, which paces requests and
retries a 429 instead of letting it propagate.
"""

import logging
import random
import time
from typing import Callable, TypeVar


logger = logging.getLogger("rate_limit")
logger.setLevel(logging.INFO)

T = TypeVar("T")

# Spacing between two consecutive LLM calls. The API tolerates ~1 req/s, so 2.5s
# leaves headroom for the occasional slow burst without stretching a run.
MIN_INTERVAL_SECONDS = 2.5
MAX_ATTEMPTS = 6
BACKOFF_BASE_SECONDS = 5
BACKOFF_CAP_SECONDS = 120

_last_call_at = 0.0


def _is_rate_limit(error: Exception) -> bool:
    """Detect a 429 without importing a specific SDK's exception type."""
    status = getattr(error, "status_code", None) or getattr(error, "http_status", None)
    if status == 429:
        return True
    response = getattr(error, "response", None)
    if response is not None and getattr(response, "status_code", None) == 429:
        return True
    text = str(error).lower()
    return "429" in text or "rate limit" in text or "rate_limited" in text


def _throttle() -> None:
    global _last_call_at
    elapsed = time.monotonic() - _last_call_at
    if elapsed < MIN_INTERVAL_SECONDS:
        time.sleep(MIN_INTERVAL_SECONDS - elapsed)
    _last_call_at = time.monotonic()


def call_with_retry(operation: Callable[[], T], description: str = "LLM call") -> T:
    """
    Run `operation`, pacing calls and retrying rate-limit errors.

    Raises the last error once the attempts are exhausted, or immediately for an
    error that is not a rate limit, so genuine failures still surface.
    """
    last_error: Exception = RuntimeError(f"{description} never ran")

    for attempt in range(MAX_ATTEMPTS):
        try:
            _throttle()
            return operation()
        except Exception as error:  # noqa: BLE001 - re-raised below
            last_error = error
            if not _is_rate_limit(error):
                raise
            if attempt == MAX_ATTEMPTS - 1:
                break
            delay = min(BACKOFF_BASE_SECONDS * (2**attempt), BACKOFF_CAP_SECONDS)
            delay *= random.uniform(0.8, 1.2)
            logger.warning(
                f"{description} rate limited (attempt {attempt + 1}/{MAX_ATTEMPTS}); "
                f"retrying in {delay:.1f}s"
            )
            time.sleep(delay)

    logger.error(f"{description} failed after {MAX_ATTEMPTS} attempts: {last_error}")
    raise last_error
