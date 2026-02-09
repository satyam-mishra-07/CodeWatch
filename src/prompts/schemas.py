from typing import List, Literal
from pydantic import BaseModel, Field


# ============================================================
# Detection
# ============================================================

class DetectedIssue(BaseModel):
    id: str = Field(..., description="Unique issue identifier")
    line_number: int = Field(..., description="Line number where issue occurs")
    issue_type: Literal[
        "logic_error",
        "potential_bug",
        "security_concern",
        "design_flaw",
        "maintainability_issue",
        "performance_concern",
    ]
    brief_description: str


class DetectionOutput(BaseModel):
    issues: List[DetectedIssue]


# ============================================================
# Explanation
# ============================================================

class ExplanationItem(BaseModel):
    issue_id: str
    why: str
    when_matters: str
    when_acceptable: str
    severity: Literal["low", "medium", "high"]
    confidence: Literal["low", "medium", "high"]


class ExplanationOutput(BaseModel):
    explanations: list[ExplanationItem]


# ============================================================
# Verification
# ============================================================

class VerificationItem(BaseModel):
    issue_id: str
    is_grounded: bool
    unstated_assumptions: List[str]
    confidence_level: Literal["low", "medium", "high"]
    recommendation: Literal["keep", "flag_uncertain", "remove"]


class VerificationOutput(BaseModel):
    verification: List[VerificationItem]