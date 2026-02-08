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

    def explain_issue(self, code: str, language: str, issue: Dict) -> Dict:
        issue_id = issue.get("id")
        self.logger.info("Explaining issue: %s", issue_id)

        prompt = build_explaination_prompt(
            code=code,
            language=language,
            issue=issue,
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

        self.logger.info("Explanation generated successfully for %s", issue_id)
        return response.model_dump()