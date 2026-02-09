import json
from typing import List

from google.genai import types

from src.agent.state import AgentState
from src.agent.tools import TOOLS
from src.agent.runtime_tools import ToolExecutor
from src.utils.logger import get_logger
from src.api.gemini_client import GeminiClient


class AgentController:
    MAX_STEPS = 8

    def __init__(self, state: AgentState):
        self.state = state
        self.logger = get_logger(self.__class__.__name__)
        self.client = GeminiClient()
        self.executor = ToolExecutor()

        self.contents: List[types.Content] = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=f"""
You are a code review agent.

Goal:
{state.goal}

Analyze the provided code and decide which tool to call next.
"""
                    )
                ],
            )
        ]

    def run(self) -> AgentState:
        self.logger.info("Agent started")

        for step in range(self.MAX_STEPS):
            self.state.increment_step()
            self.logger.info("Agent step %d", step + 1)

            # ===== Guardrail 1: must detect issues at least once =====
            if self.state.step_count == 1 and not self.state.detection_attempted and not self.state.issues:
                self.logger.info("Forcing initial detect_issues step")

                result = self.executor.execute(
                    tool_name="detect_issues",
                    state=self.state,
                    arguments={},
                )
                self._update_state("detect_issues", result)

                # 👇 Feed tool output back to the LLM
                self.contents.append(
                    types.Content(
                        role="tool",
                        parts=[
                            types.Part.from_function_response(
                                name="detect_issues",
                                response=result,
                            )
                        ],
                    )
                )

                continue

            issue_ids = {i["id"] for i in self.state.issues}
            explained_ids = {e.get("issue_id") for e in self.state.explanations}
            missing_ids = issue_ids - explained_ids

            if self.state.explanation_attempted and missing_ids and not self.state.explanation_retry_done:
                self.logger.info("Retrying explanations for missing issues")
                self.logger.warning(
                    "Incomplete explanations: %d/%d explained",
                    len(explained_ids),
                    len(issue_ids),
                )
                missing_issues = [
                    i for i in self.state.issues if i["id"] in missing_ids
                ]

                result = self.executor.execute(
                    tool_name="explain_issues",
                    state=self.state,
                    arguments={"issues": missing_issues},
                )

                self.state.explanation_retry_done = True
                self._update_state("explain_issues", result)
                continue

            if missing_ids and self.state.explanation_retry_done:
                self.logger.warning(
                    "Proceeding with partial explanations (%d/%d)",
                    len(explained_ids),
                    len(issue_ids),
                )
                     
            # ===== Guardrail 2: no issues means we're done =====
            if self.state.step_count > 1 and not self.state.issues:
                self.logger.info("No issues detected; finishing early")
                self.state.done = True
                break

            # ===== LLM decides next action =====
            assistant_content = self.client.decide_next_action(
                contents=self.contents,
                tools=TOOLS,
            )

            self.contents.append(assistant_content)

            # Execute ALL function calls
            for part in assistant_content.parts:
                if not part.function_call:
                    continue

                tool_name = part.function_call.name
                arguments = dict(part.function_call.args)

                self.logger.info(
                    "LLM requested tool: %s | args=%s",
                    tool_name,
                    arguments,
                )

                if tool_name not in self.executor.allowed_actions:
                    raise RuntimeError(f"Illegal tool call: {tool_name}")

                result = self.executor.execute(
                    tool_name=tool_name,
                    state=self.state,
                    arguments=arguments,
                )

                self._update_state(tool_name, result)

                # Feed tool result back
                self.contents.append(
                    types.Content(
                        role="tool",
                        parts=[
                            types.Part.from_function_response(
                                name=tool_name,
                                response=result,
                            )
                        ],
                    )
                )

                break  # one tool per step

            else:
                # No tool calls → agent is done
                self.logger.info("No tool call returned; finishing")
                self.state.done = True
                break

        if not self.state.done:
            self.logger.warning(
                "Agent reached max steps (%d) without explicit finish",
                self.MAX_STEPS,
            )
            self.state.done = True

        self.logger.info("Agent finished execution")
        return self.state


    def _update_state(self, tool_name: str, result: dict) -> None:
        if tool_name == "detect_issues":
            self.state.issues.extend(result.get("issues", []))
            self.state.detection_attempted = True
            self.logger.info(
                "State updated: %d issues total",
                len(self.state.issues),
            )

        elif tool_name == "explain_issues":
            self.state.explanations.extend(result["explanations"])
            self.state.explanation_attempted = True
            self.logger.info(
                "State updated: explanation added for %d issues",
                len(result.get("explanations", [])),
            )

        elif tool_name == "verify_analysis":
            self.state.verification = result
            self.logger.info("State updated: verification stored")