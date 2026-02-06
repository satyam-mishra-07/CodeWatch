import os
from typing import Optional

class LanguageDetector:
    """
    Simple language detection: user hint OR file extension
    That's it. No fancy pattern matching.
    """
    
    def __init__(self):
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
        
        Returns:
            Language name as string
        """
        
        # Strategy 1: User told us - trust them
        if user_hint:
            return self._normalize(user_hint)
        
        # Strategy 2: Check file extension
        if filename:
            lang = self._from_extension(filename)
            if lang:
                return lang
        
        # Strategy 3: We don't know - that's okay!
        return 'unknown'
    
    def _normalize(self, lang: str) -> str:
        """Handle common variations in language names"""
        lang_lower = lang.lower().strip()
        return self.aliases.get(lang_lower, lang_lower)
    
    def _from_extension(self, filename: str) -> Optional[str]:
        """Get language from file extension"""
        _, ext = os.path.splitext(filename)
        return self.extension_map.get(ext.lower())
