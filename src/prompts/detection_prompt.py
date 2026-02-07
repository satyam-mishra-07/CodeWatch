def build_detection_prompt(code: str, language: str) -> str:
    return f"""
    You are a code analysis assistant. Your task is to ONLY identify potential issues in the provided source code. DO NOT provide explanations or suggestions yet, just list the issues you find.

CODE:
```{language}
{code}
```

LANGUAGE: {language}

OUTPUT REQUIREMENTS:
- Return ONLY a JSON array of issues
- Each issue must have: id, line_number, issue_type, brief_description
- DO NOT explain WHY issues exist yet
- Focus on correctness over completeness
- If uncertain about an issue, skip it

VALID ISSUE TYPES:
- logic_error
- potential_bug
- security_concern
- design_flaw
- maintainability_issue
- performance_concern

Return ONLY valid JSON. No markdown, no explanation.
"""