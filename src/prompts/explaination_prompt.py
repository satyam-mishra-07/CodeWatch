def build_explaination_prompt(code: str, language: str, issues: list[dict]) -> str:
    return f"""You are explaining a specific code issue. Be precise and conditional.

CODE:
```{language}
{code}
```

DETECTED ISSUES:
{issues}


YOUR TASK:
Generate explanations for the detected issues.

RULES:
- Return EXACTLY ONE explanation per issue.
- Each explanation MUST correspond to one issue from DETECTED ISSUES.
- Each explanation object MUST include the SAME issue_id as the issue it explains.

Each explanation object must have:
    1. issue_id (string)
    2. why (root cause)
    3. when_matters (conditions where it's problematic)
    4. when_acceptable (when it may not matter)
    5. severity ("low" | "medium" | "high")
    6. confidence ("low" | "medium" | "high")


OUTPUT RULES:
- Return one explanation object per issue
- Each explanation MUST include issue_id matching the issue
- All issues MUST be covered exactly once
- Output must conform to the provided JSON schema
- Return ONLY valid JSON

CONSTRAINTS:
- Be specific to THIS code, not generic advice
- If you're uncertain, say so explicitly
- Don't invent facts about the codebase
- Focus on causality, not just naming the problem

Return ONLY valid JSON. No markdown, no explanation."""