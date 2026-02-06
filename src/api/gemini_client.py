from openai import OpenAI
from typing import Dict, Optional
import logging
from config.settings import settings


class GeminiClient:
    """
    Gemini API client using OpenAI SDK
    """
    
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.gemini_api_key,
            base_url=settings.gemini_base_url
        )
        self.model = settings.gemini_model
        self.logger = logging.getLogger(__name__)
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        **kwargs
    ) -> Optional[str]:
        """
        Generate content using Gemini via OpenAI SDK
        
        Args:
            prompt: The prompt to send
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
        
        Returns:
            Generated text or None if failed
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Generation failed: {str(e)}")
            return None
    
    def generate_with_retry(
        self,
        prompt: str,
        max_retries: int = 2,
        **kwargs
    ) -> Optional[str]:
        """
        Generate with automatic retry on failure
        """
        for attempt in range(max_retries):
            result = self.generate(prompt, **kwargs)
            if result:
                return result
            
            self.logger.warning(f"Attempt {attempt + 1} failed, retrying...")
        
        return None