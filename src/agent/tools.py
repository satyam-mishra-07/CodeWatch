"""
LLM-facing tool definitions for the Code Review Agent.

These definitions describe WHAT tools exist and HOW the LLM
is allowed to call them. Actual execution is handled separately.
"""

TOOLS = [
    {
        "type": "function",
        "name": "detect_issues",
        "description": (
            "Analyze the provided source code and identify potential issues. "
            "Returns a list of detected issues with line numbers and brief descriptions."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "type": "function",
        "name": "explain_issue",
        "description": (
            "Generate a detailed explanation for a specific detected issue, "
            "including why it is an issue, when it matters, and when it may be acceptable."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "issue_id": {
                    "type": "string",
                    "description": "The unique identifier of the issue to explain.",
                }
            },
            "required": ["issue_id"],
        },
    },
    {
        "type": "function",
        "name": "verify_analysis",
        "description": (
            "Review all generated issue explanations and assess their grounding, "
            "confidence level, and whether each finding should be kept or flagged as uncertain."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]
