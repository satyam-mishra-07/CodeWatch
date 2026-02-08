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

            assistant_content = self.client.decide_next_action(
                contents=self.contents,
                tools=TOOLS,
            )

            self.contents.append(assistant_content)

            # Execute ALL function calls (Gemini can emit multiple parts)
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

                # Feed tool result back to the model
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

                break  # one tool per step (agent discipline)

            else:
                # No function calls → agent is done
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
            self.logger.info(
                "State updated: %d issues total",
                len(self.state.issues),
            )

        elif tool_name == "explain_issue":
            self.state.explanations.append(result)
            self.logger.info(
                "State updated: explanation added for %s",
                result.get("issue_id"),
            )

        elif tool_name == "verify_analysis":
            self.state.verification = result
            self.logger.info("State updated: verification stored")