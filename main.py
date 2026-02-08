import argparse
import json
from pathlib import Path
from typing import Any

from config.settings import settings
from src.agent.controller import AgentController
from src.agent.state import AgentState
from src.modules.input_handler import InputHandler
from src.utils.logger import get_logger


LOGGER = get_logger("main")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the CodeWatch code-review agent on a source file.",
    )
    parser.add_argument("input_file", help="Path to source code file to analyze.")
    parser.add_argument(
        "--language",
        default=None,
        help="Optional language override (e.g., python, javascript).",
    )
    parser.add_argument(
        "--goal",
        default="Produce a high-confidence code review",
        help="Goal passed to the agent controller.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print final JSON result.",
    )
    return parser


def _state_to_dict(state: AgentState) -> dict[str, Any]:
    return {
        "goal": state.goal,
        "language": state.language,
        "issues": state.issues,
        "explanations": state.explanations,
        "verification": state.verification,
        "step_count": state.step_count,
        "done": state.done,
    }


def run_pipeline(input_file: str, language: str | None, goal: str) -> dict[str, Any]:
    file_path = Path(input_file)
    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Configure it in environment or .env before running the pipeline."
        )

    code = file_path.read_text(encoding="utf-8")
    input_handler = InputHandler()
    processed = input_handler.process(code=code, filename=file_path.name, language=language)

    state = AgentState(goal=goal, code=processed["code"], language=processed["language"])
    controller = AgentController(state=state)
    final_state = controller.run()

    return _state_to_dict(final_state)


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        result = run_pipeline(args.input_file, args.language, args.goal)
    except Exception as exc:
        LOGGER.error("Pipeline failed: %s", exc)
        print(json.dumps({"error": str(exc)}))
        return 1

    print(json.dumps(result, indent=2) if args.pretty else json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
