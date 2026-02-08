from typing import Dict
from src.api.gemini_client import GeminiClient
from src.utils.logger import get_logger
from src.prompts.detection_prompt import build_detection_prompt
from config.settings import settings
from src.prompts.schemas import DetectionOutput


class IssueDetector:
    """
    Tool: detect_issues
    Identifies potential issues in source code.
    """

    def __init__(self):
        self.client = GeminiClient()
        self.logger = get_logger(self.__class__.__name__)

    def detect_issues(self, code: str, language: str) -> Dict:
        self.logger.info("Issue detection started")

        prompt = build_detection_prompt(
            code=code,
            language=language
        )

        response = self.client.generate_structured(
            prompt=prompt,
            schema=DetectionOutput,
            temperature=settings.detection_temperature,
            max_tokens=settings.detection_max_tokens,
        )

        if not response:
            self.logger.error("Issue detection failed: empty LLM response")
            return {"issues": []}
        
        self.logger.info(
                "Issue detection completed successfully",
                extra={"issue_count": len(response.issues)}
            )

        return response.model_dump()
