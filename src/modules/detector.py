from typing import Dict
from google.genai import types
from config.settings import settings
from src.api.gemini_client import GeminiClient
from src.utils.logger import get_logger
from src.prompts.detection_prompt import build_detection_prompt
from src.prompts.schemas import DetectionOutput


class IssueDetector:
    def __init__(self):
        self.client = GeminiClient()
        self.logger = get_logger(self.__class__.__name__)

    def detect_issues(self, code: str, language: str) -> Dict:
        self.logger.info("Issue detection started")

        prompt = build_detection_prompt(code=code, language=language)

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            )
        ]

        response = self.client.generate_structured(
            contents=contents,
            schema=DetectionOutput,
            temperature=settings.detection_temperature,
            max_tokens=settings.detection_max_tokens,
        )

        self.logger.info(
            "Issue detection completed successfully | issues=%d",
            len(response.issues),
        )

        return response.model_dump()
