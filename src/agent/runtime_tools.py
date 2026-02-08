from typing import Dict, Any

from src.modules.detector import IssueDetector
from src.modules.explainer import IssueExplainer
from src.modules.verifier import AnalysisVerifier
from src.utils.logger import get_logger


class ToolExecutor:
    """
    Maps LLM tool calls → Python module execution
    """

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

        self.detector = IssueDetector()
        self.explainer = IssueExplainer()
        self.verifier = AnalysisVerifier()

        self.allowed_actions = {
            "detect_issues",
            "explain_issue",
            "verify_analysis",
        }

    def execute(
        self,
        tool_name: str,
        state,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        self.logger.info("Executing tool: %s", tool_name)

        if tool_name == "detect_issues":
            return self.detector.detect_issues(
                code=state.code,
                language=state.language,
            )

        if tool_name == "explain_issue":
            issue_id = arguments.get("issue_id")
            issue = next(
                (i for i in state.issues if i["id"] == issue_id),
                None,
            )
            if not issue:
                raise ValueError(f"Issue not found: {issue_id}")

            return self.explainer.explain_issue(
                code=state.code,
                language=state.language,
                issue=issue,
            )

        if tool_name == "verify_analysis":
            return self.verifier.verify_analysis(
                code=state.code,
                explanations=state.explanations,
            )

        raise ValueError(f"Unknown tool: {tool_name}")