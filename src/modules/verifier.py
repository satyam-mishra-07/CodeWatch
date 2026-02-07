import json
from typing import Dict, List
from src.api.gemini_client import GeminiClient
from src.utils.logger import get_logger
from src.prompts.verification_prompt import build_verification_prompt
from src.prompts.schemas import VerificationOutput


class AnalysisVerifier:
    """
    Tool: verify_analysis
    Performs confidence and grounding checks on explanations.
    """

    def __init__(self):
        self.client = GeminiClient()
        self.logger = get_logger(self.__class__.__name__)

    def verify_analysis(
        self,
        code: str,
        explanations: List[Dict]
    ) -> Dict:
        self.logger.info("Verification started")

        prompt = build_verification_prompt(
            code=code,
            explanations=explanations
        )

        response = self.client.generate_structured(
            prompt=prompt,
            schema=VerificationOutput,
            temperature=0.2,
            max_tokens=1024,
        )

        if not response:
            self.logger.error("Verification failed: empty LLM response")
            return {}

        self.logger.info(
                "Verification completed for %d issues",
                len(explanations)
            )
        
        return response.model_dump()
        