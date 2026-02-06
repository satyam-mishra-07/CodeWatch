import os
from typing import Optional
from src.utils.language_detector import LanguageDetector



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