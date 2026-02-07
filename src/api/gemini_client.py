from openai import OpenAI
from typing import Dict, Optional
from config.settings import settings
from src.utils.logger import get_logger
from typing import Type, TypeVar
from pydantic import BaseModel
from src.utils.logger import get_logger

T = TypeVar("T", bound=BaseModel)


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
        self.logger = get_logger(self.__class__.__name__)

    def generate(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        **kwargs
    ) -> Optional[str]:
        """
        Generate content using Gemini via OpenAI SDK
        """
        self.logger.info(
            "LLM generation request | model=%s | temperature=%.2f | max_tokens=%d",
            self.model,
            temperature,
            max_tokens,
        )

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

            self.logger.info("LLM generation succeeded")
            return response.choices[0].message.content

        except Exception as e:
            self.logger.error("Generation failed: %s", str(e))
            return None

    def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> T:
        """
        Generate structured output using response_format (JSON Schema).
        """

        self.logger.info(
            "LLM structured generation | model=%s | schema=%s",
            self.model,
            schema.__name__,
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={
                "type": "json_schema",
                "json_schema": schema.model_json_schema(),
            },
        )

        content = response.choices[0].message.content

        if content is None:
            raise RuntimeError("Structured generation returned empty content")

        # This SHOULD already be schema-compliant
        return schema.model_validate_json(content)


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

            self.logger.warning(
                "LLM generation attempt %d/%d failed, retrying...",
                attempt + 1,
                max_retries,
            )

        self.logger.error("All LLM generation attempts failed")
        return None