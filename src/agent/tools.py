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

explain_issues_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="explain_issues",
            description=(
                "Generate detailed explanations for ALL detected issues in the code."
            ),
            parameters={
                "type": "object",
                "properties": {},
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
    explain_issues_tool,
    verify_analysis_tool,
]
