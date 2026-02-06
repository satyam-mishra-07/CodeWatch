import os
from typing import Optional, Tuple


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


class InputHandler:
    """
    Handle code input with format preservation and simple language detection
    """
    
    def __init__(self):
        self.detector = LanguageDetector()
    
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
        
        # Validate
        if not code or not code.strip():
            raise ValueError("Code cannot be empty")
        
        # Detect language
        detected_lang = self.detector.detect(
            filename=filename,
            user_hint=language
        )
        
        return {
            'code': code,  # Never modified
            'language': detected_lang
        }


# Usage Examples
if __name__ == "__main__":
    handler = InputHandler()
    
    # Example 1: From file (extension detection)
    code1 = "def hello():\n    print('Hi')"
    result = handler.process(code1, filename="test.py")
    print(result)  # {'code': '...', 'language': 'python'}
    
    # Example 2: User specifies
    code2 = "function hello() { }"
    result = handler.process(code2, language="javascript")
    print(result)  # {'code': '...', 'language': 'javascript'}
    
    # Example 3: Can't detect - that's fine!
    code3 = "some code here"
    result = handler.process(code3)
    print(result)  # {'code': '...', 'language': 'unknown'}