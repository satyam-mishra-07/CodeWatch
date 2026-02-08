from typing import Type, TypeVar, List

from pydantic import BaseModel
from google import genai
from google.genai import types

from config.settings import settings
from src.utils.logger import get_logger

T = TypeVar("T", bound=BaseModel)


class GeminiClient:
    """Gemini-native client with tool calling + structured output."""

    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model
        self.logger = get_logger(self.__class__.__name__)

    # --------------------------------------------------
    # Tool-decision step (agent reasoning)
    # --------------------------------------------------
    def decide_next_action(
        self,
        contents: List[types.Content],
        tools: List[types.Tool],
    ) -> types.Content:
        self.logger.info("LLM deciding next tool to call")

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(
                tools=tools,
            ),
        )

        return response.candidates[0].content

    # --------------------------------------------------
    # Structured output generation
    # --------------------------------------------------
    def generate_structured(
        self,
        contents: List[types.Content],
        schema: Type[T],
        temperature: float,
        max_tokens: int,
    ) -> T:
        self.logger.info(
            "LLM structured generation | schema=%s",
            schema.__name__,
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema.model_json_schema(),
            ),
        )

        return schema.model_validate_json(response.text)
