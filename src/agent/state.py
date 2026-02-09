from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class AgentState:
    goal: str
    code: str
    language: str

    detection_attempted: bool = False

    issues: List[Dict] = field(default_factory=list)
    explanations: List[Dict] = field(default_factory=list)
    verification: Optional[Dict] = None

    step_count: int = 0
    done: bool = False

    explanation_retry_done: bool = False
    explanation_attempted: bool = False

    def increment_step(self):
        self.step_count += 1
