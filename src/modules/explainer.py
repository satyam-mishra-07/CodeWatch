import json
from typing import Dict
from src.api.gemini_client import GeminiClient
from src.utils.logger import get_logger
from src.prompts.explaination_prompt import build_explaination_prompt
from src.prompts.schemas import ExplanationOutput


class IssueExplainer:
    """
    Tool: explain_issue
    Generates a detailed explanation for a specific issue.
    """

    def __init__(self):
        self.client = GeminiClient()
        self.logger = get_logger(self.__class__.__name__)

    def explain_issue(
        self,
        code: str,
        language: str,
        issue: Dict
    ) -> Dict:
        issue_id = issue.get("id")
        self.logger.info("Explaining issue: %s", issue_id)

        prompt = build_explaination_prompt(
            code=code,
            language=language,
            issue=issue
        )

        response = self.client.generate_structured(
            prompt=prompt,
            schema=ExplanationOutput,
            temperature=0.4,
            max_tokens=1024,
        )

        if not response:
            self.logger.error(
                "Explanation failed: empty response for issue %s",
                issue_id
            )
            return {}
        
        self.logger.info(
                "Explanation generated successfully for issue %s",
                issue_id
            )
        
        return response.model_dump()