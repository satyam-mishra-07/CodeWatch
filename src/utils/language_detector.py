import os
from typing import Optional
from src.utils.logger import get_logger


class LanguageDetector:
    """
    Simple language detection: user hint OR file extension
    That's it. No fancy pattern matching.
    """

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

        # Extension to language mapping
        self.extension_map = {
            '.py': 'python',
            '.pyw': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.cs': 'csharp',
            '.sql': 'sql',
            '.sh': 'bash',
            '.r': 'r',
            '.scala': 'scala',
        }

        # Language name normalization (for user input)
        self.aliases = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'c++': 'cpp',
            'c#': 'csharp',
            'golang': 'go',
            'sh': 'bash',
            'shell': 'bash',
        }

    def detect(
        self,
        filename: Optional[str] = None,
        user_hint: Optional[str] = None
    ) -> str:
        """
        Detect language using two simple strategies

        Priority:
        1. User hint (if provided)
        2. File extension (if filename provided)
        3. 'unknown' (give up gracefully)
        """

        self.logger.debug(
            "Starting language detection | filename=%s | user_hint=%s",
            filename,
            user_hint,
        )

        # Strategy 1: User told us - trust them
        if user_hint:
            normalized = self._normalize(user_hint)
            self.logger.info(
                "Language detected from user hint: %s -> %s",
                user_hint,
                normalized,
            )
            return normalized

        # Strategy 2: Check file extension
        if filename:
            lang = self._from_extension(filename)
            if lang:
                self.logger.info(
                    "Language detected from file extension: %s -> %s",
                    filename,
                    lang,
                )
                return lang

        # Strategy 3: We don't know - that's okay!
        self.logger.warning("Language detection failed: returning 'unknown'")
        return 'unknown'

    def _normalize(self, lang: str) -> str:
        """Handle common variations in language names"""
        lang_lower = lang.lower().strip()
        normalized = self.aliases.get(lang_lower, lang_lower)

        if lang_lower != normalized:
            self.logger.debug(
                "Normalized language alias: %s -> %s",
                lang_lower,
                normalized,
            )

        return normalized

    def _from_extension(self, filename: str) -> Optional[str]:
        """Get language from file extension"""
        _, ext = os.path.splitext(filename)
        lang = self.extension_map.get(ext.lower())

        if lang:
            self.logger.debug(
                "Matched extension %s to language %s",
                ext,
                lang,
            )
        else:
            self.logger.debug(
                "No language mapping found for extension %s",
                ext,
            )

        return lang
