# CodeWatch

CodeWatch is an agentic code-review pipeline that uses Gemini (via the OpenAI-compatible SDK) to:
1. detect potential issues,
2. explain each issue,
3. verify confidence/grounding.

It includes a runnable CLI (`main.py`) and a deterministic `--dry-run` mode for local validation without API calls.

## Architecture

The implementation follows the agent-loop plan in `IMPLEMENTATION_PLAN.md`:
- **Input handling**: validate code and detect language.
- **Agent controller**: iterative tool-calling loop.
- **Tools**:
  - `detect_issues`
  - `explain_issue`
  - `verify_analysis`
- **State**: shared `AgentState` object across loop steps.

Key runtime modules:
- `src/agent/controller.py`
- `src/agent/runtime_tools.py`
- `src/modules/{detector,explainer,verifier,input_handler}.py`
- `src/api/gemini_client.py`

## Requirements

- Python 3.10+
- Gemini API key (`GEMINI_API_KEY`) for live runs

Install:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Set environment variables (or use a `.env` file at repo root):

```bash
export GEMINI_API_KEY="your_key"
export GEMINI_MODEL="gemini-3-flash-preview"
```

Primary settings live in `config/settings.py`.

## Usage

### 1) Dry run (no API calls)

Use this to validate the full pipeline wiring and output schema:

```bash
python main.py path/to/file.py --dry-run --pretty
```

### 2) Live run (calls Gemini)

```bash
python main.py path/to/file.py --pretty
```

Optional flags:
- `--language python` to force language
- `--goal "Produce a high-confidence code review"`

## Output

`main.py` prints JSON with:
- `goal`
- `language`
- `issues`
- `explanations`
- `verification`
- `step_count`
- `done`

## Development Notes

- Logging is configured in `src/utils/logger.py`.
- Prompt builders are in `src/prompts/`.
- Pydantic schemas for tool outputs are in `src/prompts/schemas.py`.

## Validation Commands

```bash
python -m py_compile $(rg --files -g '*.py')
pytest -q
python main.py README.md --dry-run --pretty
```

> Note: current test files are placeholders; `pytest` may report that no tests were collected.
