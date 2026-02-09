# CodeWatch

**Agentic code review pipeline that detects issues, explains impact, and verifies confidence using Gemini.**

## What problem this solves

Code reviews are often inconsistent: some findings are shallow, some are vague, and confidence is rarely explicit. CodeWatch solves this by enforcing a structured, multi-step review flow:

- detect concrete issues first,
- explain each issue in context,
- verify grounding/confidence before returning final results.

This makes outputs more actionable than a single-pass “spot check.”

## What it does (capabilities)

- Analyzes a source file from the CLI.
- Detects language via user hint or file extension.
- Uses tool-based agent actions:
  - `detect_issues`
  - `explain_issues`
  - `verify_analysis`
  - `finish`
- Produces structured JSON with issues, explanations, verification, and execution metadata.
- Applies guardrails to avoid incomplete flows (e.g., force initial detection, retry missing explanations once).

## How the agent works (money section)

CodeWatch uses an explicit **stateful agent loop** (`AgentController`) rather than one monolithic prompt.

### 1) Input processing

`main.py` reads the input file, validates it, and delegates preprocessing to `InputHandler`.

`InputHandler`:
- validates non-empty code,
- enforces max code length from settings,
- detects language from hint/extension.

### 2) Shared state initialization

The agent creates `AgentState`, which tracks:
- goal,
- code,
- language,
- detected issues,
- explanations,
- verification,
- step counters and retry flags.

### 3) Controlled multi-step loop

`AgentController.run()` executes up to `MAX_STEPS=8`:

- **Guardrail A:** On step 1, it forces `detect_issues` if detection has not been attempted.
- **Guardrail B:** If no issues are found after initial pass, it exits early.
- Otherwise, Gemini decides the next tool call using function-calling.
- Tool calls are validated against allowed actions before execution.

### 4) Tool execution + state updates

`ToolExecutor` dispatches to runtime modules:
- `Detector` → issue list
- `Explainer` → per-issue reasoning fields
- `Verifier` → groundedness/confidence checks

After each tool call, the result is:
1. merged into `AgentState`, and
2. fed back to Gemini as a tool response so the next step can reason over fresh state.

### 5) Reliability behavior

- If explanations are missing for some issue IDs, the controller retries `explain_issues` once with only missing issues.
- If still partial, it proceeds with warnings instead of hard failing.
- If Gemini returns no tool call, the agent marks execution complete.

This pattern gives deterministic control over workflow while still letting the model choose the next action.

## Architecture overview

```text
main.py (CLI)
  └── InputHandler (validate + language detect)
      └── AgentState
          └── AgentController loop
              ├── GeminiClient (decide next tool call)
              ├── ToolExecutor
              │   ├── Detector
              │   ├── Explainer
              │   └── Verifier
              └── finish
```

Core directories:

- `src/agent/` → controller, state, tool registry/execution
- `src/modules/` → detector/explainer/verifier/input handling modules
- `src/prompts/` → prompt builders + output schemas
- `src/api/` → Gemini client wrapper
- `src/utils/` → logging + language detection
- `config/` → runtime settings via environment

## Tech stack

- **Language:** Python 3.10+
- **LLM access:** Google Gemini via `google-genai`
- **Configuration:** `pydantic-settings`
- **Data validation/schema:** `pydantic`
- **CLI:** `argparse` (stdlib)
- **Testing support:** `pytest`

## How to run locally

### 1) Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Configure environment

```bash
cp .env.example .env
# then set GEMINI_API_KEY in .env
```

Minimum required variable:

```env
GEMINI_API_KEY=your_real_key_here
```

Optional tuning (already in `.env.example`): model, temperatures, token limits, feature flags, and limits.

### 3) Run

```bash
python main.py example/smoke_test.js --pretty
```

Optional flags:

- `--language javascript` to override auto-detection
- `--goal "Produce a high-confidence code review"` to customize agent objective

## Example output

Below is representative output structure (values abbreviated):

```json
{
  "goal": "Produce a high-confidence code review",
  "language": "javascript",
  "issues": [
    {
      "id": "ISSUE-1",
      "line_number": 10,
      "issue_type": "potential_bug",
      "brief_description": "user is undefined before property assignment"
    }
  ],
  "explanations": [
    {
      "issue_id": "ISSUE-1",
      "why": "The code writes user.name before user is initialized.",
      "when_matters": "Runtime crashes when id > 0.",
      "when_acceptable": "Only if user is guaranteed initialized beforehand.",
      "severity": "high",
      "confidence": "high"
    }
  ],
  "verification": {
    "verification": [
      {
        "issue_id": "ISSUE-1",
        "is_grounded": true,
        "unstated_assumptions": [],
        "confidence_level": "high",
        "recommendation": "keep"
      }
    ]
  },
  "step_count": 4,
  "done": true
}
```

---

If you want, I can also add a quick **"Troubleshooting"** section (common API key/config errors) and a **"Contributing"** section next.
