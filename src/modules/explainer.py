from typing import Dict
from google.genai import types
from config.settings import settings
from src.api.gemini_client import GeminiClient
from src.utils.logger import get_logger
from src.prompts.explaination_prompt import build_explaination_prompt
from src.prompts.schemas import ExplanationOutput


class IssueExplainer:
    def __init__(self):
        self.client = GeminiClient()
        self.logger = get_logger(self.__class__.__name__)

    def explain_issues(self, code: str, language: str, issues: list[Dict]) -> Dict:
        issue_id = issues[0].get("id") if issues else None
        self.logger.info("Explaining %d issues in batch", len(issues))

        prompt = build_explaination_prompt(
            code=code,
            language=language,
            issues=issues,
        )

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            )
        ]

        response = self.client.generate_structured(
            contents=contents,
            schema=ExplanationOutput,
            temperature=settings.explanation_temperature,
            max_tokens=settings.explanation_max_tokens,
        )

        self.logger.info(
            "Batch explanation generated successfully (%d issues)",
            len(response.explanations),
        )
        return response.model_dump()