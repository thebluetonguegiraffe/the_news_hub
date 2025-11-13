import requests


class TranslationError(Exception):
    pass


class GoogleTranslator:
    BASE_URL = "https://translate.googleapis.com/translate_a/single"

    def __init__(self, source_lang: str = None):
        """Initialize Google Translator with cache"""
        self.session = requests.Session()
        self.source_lang = source_lang

    def translate(self, text: str, target_lang: str) -> str:
        if not text:
            raise TranslationError("Text cannot be empty")

        params = {
            "client": "gtx",
            "sl": self.source_lang,
            "tl": target_lang,
            "dt": "t",
            "q": text.strip(),
        }

        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            translated = "".join([sentence[0] for sentence in data[0] if sentence[0]])

            return translated

        except requests.exceptions.RequestException as e:
            raise TranslationError(f"Network error: {str(e)}")
        except (KeyError, IndexError, ValueError) as e:
            raise TranslationError(f"Failed to parse response: {str(e)}")
        except Exception as e:
            raise TranslationError(f"Translation failed: {str(e)}")

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
        except Exception as e:
            raise TranslationError(f"Translation failed: {str(e)}")


if __name__ == "__main__":
    translator = GoogleTranslator("en")

    print("=== Google Translator Demo ===\n")

    result = translator.translate("Hello, how are you?", target_lang="es")
    print(f"Translation: {result}")
