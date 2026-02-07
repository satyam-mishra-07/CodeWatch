import json


def build_verification_prompt(code: str, explanations: list) -> str:
    explanations_json = json.dumps(explanations, indent=2)
    return f"""You are reviewing code analysis outputs for quality and certainty.

ORIGINAL CODE:
{code}

ANALYSIS RESULTS:
{explanations_json}

YOUR TASK:
For each issue, assess:
1. Is the explanation grounded in the actual code?
2. Are there dependencies or assumptions not stated?
3. What is your confidence level in this assessment?

Return ONLY valid JSON."""