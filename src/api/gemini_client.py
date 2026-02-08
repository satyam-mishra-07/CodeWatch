from typing import Type, TypeVar

from openai import OpenAI
from pydantic import BaseModel

from config.settings import settings
from src.utils.logger import get_logger

T = TypeVar("T", bound=BaseModel)


class GeminiClient:
    """Minimal Gemini API client used by agent tools/controller."""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.gemini_api_key,
            base_url=settings.gemini_base_url,
        )
        self.model = settings.gemini_model
        self.logger = get_logger(self.__class__.__name__)

    def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        temperature: float,
        max_tokens: int,
    ) -> T:
        """Generate schema-validated JSON output from Gemini."""
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

        return schema.model_validate_json(content)
    def create_tool_decision(self, messages: list[dict], tools: list[dict]):
        """Create one tool-calling decision step for the agent loop."""
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.1,
            max_tokens=512,
        )

