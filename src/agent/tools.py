from google.genai import types

detect_issues_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="detect_issues",
            description=(
                "Analyze the provided source code and identify potential issues. "
                "Returns a list of detected issues with line numbers and brief descriptions."
            ),
            parameters={
                "type": "object",
                "properties": {},
            },
        )
    ]
)

explain_issue_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="explain_issue",
            description=(
                "Generate a detailed explanation for a specific detected issue, "
                "including why it is an issue, when it matters, and when it may be acceptable."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "issue_id": {
                        "type": "string",
                        "description": "The unique identifier of the issue to explain.",
                    }
                },
                "required": ["issue_id"],
            },
        )
    ]
)

verify_analysis_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="verify_analysis",
            description=(
                "Review all generated issue explanations and assess their grounding, "
                "confidence level, and whether each finding should be kept or flagged as uncertain."
            ),
            parameters={
                "type": "object",
                "properties": {},
            },
        )
    ]
)

TOOLS = [
    detect_issues_tool,
    explain_issue_tool,
    verify_analysis_tool,
]
