def build_explaination_prompt(code: str, language: str, issue: dict) -> str:
    return f"""You are explaining a specific code issue. Be precise and conditional.

CODE:
```{language}
{code}
```

ISSUE:
ID: {issue['id']}
Line: {issue['line_number']}
Type: {issue['issue_type']}
Description: {issue['brief_description']}

YOUR TASK:
Explain this issue in three parts:

1. WHY this is an issue (root cause)
2. WHEN it matters (conditions where it's problematic)
3. WHEN it may NOT matter (acceptable contexts)

CONSTRAINTS:
- Be specific to THIS code, not generic advice
- If you're uncertain, say so explicitly
- Don't invent facts about the codebase
- Focus on causality, not just naming the problem

Return ONLY valid JSON. No markdown, no explanation."""