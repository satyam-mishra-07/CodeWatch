import json
from typing import List

from src.agent.state import AgentState
from src.agent.tools import TOOLS
from src.agent.runtime_tools import ToolExecutor
from src.utils.logger import get_logger
from src.utils.validators import Validator
from src.api.gemini_client import GeminiClient


class AgentController:
    MAX_STEPS = 8

    def __init__(self, state: AgentState):
        self.state = state
        self.logger = get_logger(self.__class__.__name__)
        self.client = GeminiClient()
        self.executor = ToolExecutor()
        self.validator = Validator()

        # Conversation history (OpenAI-style)
        self.messages: List[dict] = [
            {
                "role": "user",
                "content": f"""
You are a code review agent.

Goal:
{state.goal}

Analyze the provided code and decide which tools to use.
"""
            }
        ]

    def run(self) -> AgentState:
        self.logger.info("Agent started")

        for step in range(self.MAX_STEPS):
            self.logger.info("Agent step %d", step + 1)

            response = self.client.client.chat.completions.create(
                model=self.client.model,
                messages=self.messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.1,
                max_tokens=512,
            )

            message = response.choices[0].message
            self.messages.append(message)

            # If the model decided to call tools
            if message.tool_calls:
                for call in message.tool_calls:
                    tool_name = call.function.name
                    arguments = json.loads(call.function.arguments or "{}")

                    self.logger.info(
                        "LLM requested tool: %s | args=%s",
                        tool_name,
                        arguments,
                    )

                    if tool_name not in self.executor.allowed_actions:
                        raise RuntimeError(f"Illegal tool call: {tool_name}")

                    # Execute tool in Python
                    result = self.executor.execute(
                        tool_name=tool_name,
                        state=self.state,
                        arguments=arguments,
                    )

                    # Update state explicitly
                    self._update_state(tool_name, result)

                    # Feed tool output back to the LLM
                    self.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": json.dumps(result),
                        }
                    )

                continue

            # No tool calls → model is done
            self.logger.info("No tool calls returned; finishing")
            self.state.done = True
            break

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