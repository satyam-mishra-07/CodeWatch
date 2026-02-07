from typing import Dict, Set, Any, Optional
from utils.logger import get_logger
import logging


class Validator:
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Validator for agent decisions and tool outputs.

        This class performs strict boundary validation to prevent
        malformed or unsafe data from entering the agent state.
        """
        self.logger = logger or get_logger(self.__class__.__name__)

    # ---------------------------------------------------------
    # Agent decision validation
    # ---------------------------------------------------------

    def validate_action(self, action: Dict[str, Any], allowed_actions: Set[str]) -> bool:
        """
        Validate agent decision action.

        Expected shape:
        {
            "action": "<action_name>",
            "issue_id": "optional",
            "reason": "optional"
        }
        """

        if not isinstance(action, dict):
            self.logger.error("Action validation failed: action is not a dict")
            return False

        if "action" not in action:
            self.logger.error("Action validation failed: missing 'action' key")
            return False

        action_name = action["action"]

        if not isinstance(action_name, str):
            self.logger.error("Action validation failed: 'action' is not a string")
            return False

        if action_name not in allowed_actions:
            self.logger.error(
                "Action validation failed: '%s' not in allowed actions %s",
                action_name,
                allowed_actions,
            )
            return False

        self.logger.info("Action validated successfully: %s", action_name)
        return True

    # ---------------------------------------------------------
    # Detection tool output validation
    # ---------------------------------------------------------

    def validate_detection_output(self, result: Dict[str, Any]) -> bool:
        """
        Validate output of detect_issues tool.

        Expected shape:
        {
            "issues": [
                {
                    "id": str,
                    "line_number": int,
                    "issue_type": str,
                    "brief_description": str
                }
            ]
        }
        """

        if not isinstance(result, dict):
            self.logger.error("Detection output validation failed: result is not a dict")
            return False

        if "issues" not in result:
            self.logger.error("Detection output validation failed: missing 'issues' key")
            return False

        issues = result["issues"]

        if not isinstance(issues, list):
            self.logger.error("Detection output validation failed: 'issues' is not a list")
            return False

        required_fields = {"id", "line_number", "issue_type", "brief_description"}

        for idx, issue in enumerate(issues):
            if not isinstance(issue, dict):
                self.logger.error(
                    "Detection output validation failed: issue at index %d is not a dict",
                    idx,
                )
                return False

            missing = required_fields - issue.keys()
            if missing:
                self.logger.error(
                    "Detection output validation failed: issue at index %d missing fields %s",
                    idx,
                    missing,
                )
                return False

        self.logger.info(
            "Detection output validated successfully: %d issues", len(issues)
        )
        return True

    # ---------------------------------------------------------
    # Explanation tool output validation
    # ---------------------------------------------------------

    def validate_explanation_output(self, result: Dict[str, Any]) -> bool:
        """
        Validate output of explain_issue tool.

        Expected shape:
        {
            "issue_id": str,
            "explanation": {
                "why": str,
                "when_matters": str,
                "when_acceptable": str,
                "severity": str,
                "confidence": str
            }
        }
        """

        if not isinstance(result, dict):
            self.logger.error("Explanation output validation failed: result is not a dict")
            return False

        if "issue_id" not in result:
            self.logger.error(
                "Explanation output validation failed: missing 'issue_id'"
            )
            return False

        if "explanation" not in result:
            self.logger.error(
                "Explanation output validation failed: missing 'explanation'"
            )
            return False

        explanation = result["explanation"]

        if not isinstance(explanation, dict):
            self.logger.error(
                "Explanation output validation failed: 'explanation' is not a dict"
            )
            return False

        required_fields = {
            "why",
            "when_matters",
            "when_acceptable",
            "severity",
            "confidence",
        }

        missing = required_fields - explanation.keys()
        if missing:
            self.logger.error(
                "Explanation output validation failed: missing fields %s", missing
            )
            return False

        self.logger.info(
            "Explanation output validated successfully for issue_id=%s",
            result.get("issue_id"),
        )
        return True
