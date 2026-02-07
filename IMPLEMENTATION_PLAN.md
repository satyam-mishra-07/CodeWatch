# Code Review Agent — Revised Agentic Implementation Plan

## 1) System Architecture

### High-Level Architecture (Agentic)

```text
┌─────────────────────┐
│   User Input        │
│  (Code + Context)   │
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│   Agent Controller  │
│  (LLM Decision Loop)│
└─────────┬───────────┘
          ▼
┌──────────────────────────────────────────┐
│              Tool Registry               │
│ ┌──────────┐ ┌──────────┐ ┌───────────┐ │
│ │ Detector │ │ Explainer│ │ Verifier  │ │
│ └──────────┘ └──────────┘ └───────────┘ │
└──────────────────────────────────────────┘
          ▼
┌─────────────────────┐
│   Output Formatter  │
└─────────────────────┘
```

### Agent Controller

The Agent Controller is responsible for agent execution and is the core of the system.

Responsibilities:
- Maintains shared agent state
- Determines next action based on goal and current state
- Invokes tools dynamically through the tool registry
- Decides when the task is complete (`finish` action)

---

## 2) Core Modules (Reframed as Tools + Runtime Components)

| Component | Revised Role |
|---|---|
| Input Module | Pre-agent initialization (parse input, validate, detect language) |
| Detection Module | Tool: `detect_issues` |
| Explanation Module | Tool: `explain_issue` |
| Verification Module | Tool: `verify_analysis` |
| Output Module | Post-agent formatting |
| Agent Controller | Decision-maker that selects actions in loop |
| Tool Registry | Runtime interface exposing available tools |

Notes:
- Tools should be stateless and operate from current state inputs.
- Statefulness belongs to the Agent Controller via the Agent State object.

---

## 3) Agent State (Mandatory)

Canonical state object:

```json
{
  "goal": "Produce a high-confidence code review",
  "code": "string",
  "language": "string",
  "issues": [],
  "explanations": [],
  "verification": null,
  "confidence": null,
  "step_count": 0,
  "done": false
}
```

State model rules:
- State persists across tool calls
- Tools may read and write state (through controlled updates)
- Tools may not delete or overwrite prior state entries, only append or annotate results.
- LLM reasoning is grounded in current state snapshot
- `step_count` supports loop limits and safety checks
- `done` is set only by valid completion logic

---

## 4) Decision Loop Design (Replaces Fixed Workflow)

### Agent Execution Loop

The system operates as a goal-driven agent. At each step, the agent:
1. Observes current state
2. Decides next action
3. Executes selected tool
4. Updates state
5. Evaluates whether goal is complete

Pseudo-flow:

```python
while not goal_satisfied:
    decide_next_action(state)
    execute_selected_tool(state)
    update_state(state)
```

### Allowed Agent Actions (explicit)
- `detect_issues`
- `explain_issue(issue_id)`
- `verify_analysis`
- `finish`

Action constraints:
- Prevent explanation before issue detection
- Skip verification if confidence is already high and sufficient
- Finish early when no issues are detected
- Reject illegal or redundant actions and force re-decision

---

## 5) Tool Specifications (Tool Results, not Phase Outputs)

### Tool: `detect_issues`
Input:
- `code`
- `language`

Tool result:
```json
{
  "issues": [
    {
      "id": "issue_1",
      "line_number": 42,
      "issue_type": "logic_error",
      "brief_description": "Null pointer dereference possible"
    }
  ]
}
```

Failure behavior:
- Retry bounded times
- On failure return empty issues + structured error marker

### Tool: `explain_issue(issue_id)`
Input:
- Full code
- Selected issue details
- language

Tool result:
```json
{
  "issue_id": "issue_1",
  "explanation": {
    "why": "...",
    "when_matters": "...",
    "when_acceptable": "...",
    "severity": "low|medium|high",
    "confidence": "low|medium|high"
  }
}
```

### Tool: `verify_analysis`
Input:
- code
- issues + explanations

Tool result:
```json
{
  "verification": [
    {
      "issue_id": "issue_1",
      "is_grounded": true,
      "unstated_assumptions": [],
      "confidence_level": "low|medium|high",
      "recommendation": "keep|flag_uncertain|remove"
    }
  ]
}
```

### Post-Agent Formatter
- Converts final state into JSON / Markdown / HTML report
- Applies optional filters by severity and confidence

---

## 6) Prompt Engineering

### Existing Tool Prompts (keep)
- Detection Prompt
- Explanation Prompt
- Verification Prompt

### New Prompt Type: Agent Decision Prompt (mandatory)

Purpose:
- Decide which tool/action to invoke next
- Enforce action legality and sequencing constraints
- Prevent invalid transitions

Decision prompt must receive:
- Entire current agent state
- Allowed actions list
- Tool/action constraints

Decision prompt must return structured action JSON:

```json
{
  "action": "detect_issues|explain_issue|verify_analysis|finish",
  "issue_id": "optional_issue_id",
  "reason": "short grounded rationale"
}
```

Required behaviors:
- Block `explain_issue` when `issues` is empty
- Prefer `finish` when `issues` is empty after detection
- Skip `verify_analysis` when confidence is already sufficient
- Avoid redundant tool calls

Temperature guidance:
- Decision prompt: very low temperature (consistency-first)
- Tool prompts: task-appropriate temperature

---

## 7) API Integration Strategy (clarified)

The LLM is used both for tool results and decision-making.

Guidance:
- Decision calls use very low temperature for deterministic behavior
- Tool calls use task-specific temperatures
- Maintain strict structured JSON outputs for both decisions and tool results
- Keep bounded retries and graceful degradation for malformed responses

---

## 8) Revised Implementation Phases

### Phase 1 (Revised)
- Core modules (existing plan scope)
- Tool wrappers for detector/explainer/verifier
- Agent state model definition and state update helpers
- Agent decision prompt implementation

### Phase 2
- Agent loop execution runtime
- Tool selection logic and action validation
- Step limits and safety checks (max steps, illegal action guardrails)

### Phase 3+
- Output/reporting capabilities (JSON/Markdown/HTML)
- Integration and CLI
- Evaluation framework expansion
- Documentation and operational hardening

---

## 9) Evaluation Framework (Agent-Specific Additions)

Keep prior quality metrics (precision, recall, consistency, hallucination), and add:

| Metric | Description |
|---|---|
| Tool Correctness | Did the agent select only valid tools/actions? |
| Step Efficiency | Average number of decision-loop steps to completion |
| Early Stop Accuracy | Did the agent stop when appropriate? |
| Redundant Tool Calls | Count of unnecessary repeated actions |
| Recovery Behavior | Ability to recover after uncertainty/invalid outputs |

These metrics are required to justify agentic behavior claims.

---

## 10) Terminology Policy (for consistency and honesty)

Use these terms consistently throughout docs and implementation notes:
- “pipeline execution” → **agent execution**
- “phase output” → **tool result**
- “workflow” → **decision loop**

This document intentionally uses agent-first terminology.

---

## 11) Practical Notes for Current Repository

- `generate_with_retry` in `GeminiClient` remains acceptable as tool-level robustness.
- Standalone `retry_logic.py` is optional and can remain scrapped if retry behavior stays centralized in client/tool wrappers.
- Existing module files can stay in place; this revision is primarily architectural and orchestration-focused.

