from typing import Optional
from src.utils.language_detector import LanguageDetector
from src.utils.logger import get_logger


class InputHandler:
    """
    Handle code input with format preservation and simple language detection
    """

    def __init__(self):
        self.detector = LanguageDetector()
        self.logger = get_logger(self.__class__.__name__)

    def process(
        self,
        code: str,
        filename: Optional[str] = None,
        language: Optional[str] = None
    ) -> dict:
        """
        Process code input

        Args:
            code: Source code (preserved exactly as-is)
            filename: Optional filename (for extension detection)
            language: Optional user-provided language

        Returns:
            {
                'code': str,       # Original unchanged code
                'language': str,   # Detected language
            }
        """

        self.logger.info(
            "Processing input | filename=%s | user_language_hint=%s",
            filename,
            language,
        )

        # Validate
        if not code or not code.strip():
            self.logger.error("Input validation failed: empty or whitespace-only code")
            raise ValueError("Code cannot be empty")

        self.logger.debug("Input validation passed (code length=%d)", len(code))

        # Detect language
        detected_lang = self.detector.detect(
            filename=filename,
            user_hint=language
        )

        self.logger.info("Language detected: %s", detected_lang)

        return {
            "code": code,        # Never modified
            "language": detected_lang
        }
