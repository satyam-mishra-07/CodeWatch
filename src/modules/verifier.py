from typing import Dict, List
from google.genai import types
from config.settings import settings
from src.api.gemini_client import GeminiClient
from src.utils.logger import get_logger
from src.prompts.verification_prompt import build_verification_prompt
from src.prompts.schemas import VerificationOutput


class AnalysisVerifier:
    def __init__(self):
        self.client = GeminiClient()
        self.logger = get_logger(self.__class__.__name__)

    def verify_analysis(self, code: str, explanations: List[Dict]) -> Dict:
        self.logger.info("Verification started")

        prompt = build_verification_prompt(
            code=code,
            explanations=explanations,
        )

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            )
        ]

        response = self.client.generate_structured(
            contents=contents,
            schema=VerificationOutput,
            temperature=settings.verification_temperature,
            max_tokens=settings.verification_max_tokens,
        )

        self.logger.info(
            "Verification completed for %d issues",
            len(response.verification),
        )

        return response.model_dump()