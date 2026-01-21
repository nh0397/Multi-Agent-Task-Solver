# Multi-Agent Task Solver

This system is a **Multi-Agent Task Solver** designed to interpret high-level user requests, break them down into executable sub-tasks, and orchestrate specialized agents to deliver a comprehensive result.

For this implementation, the system is specifically scoped to the **Financial Domain** to demonstrate deep context retrieval and analysis.

## The Architecture

A **Planner-Supervisor** pattern is utilized to handle ambiguity and ensure execution accuracy.

### 1. The Planner (Gatekeeper)

The entry point for all requests. It evaluates the user's input for clarity.

- **Ambiguity Check**: If the request is vague (e.g., "How is the stock?"), it halts execution and asks clarifying questions.
- **Plan Generation**: If the request is clear, it generates a structured `ExecutionPlan`.

### 2. The Supervisor (Manager)

A stateful orchestrator that executes the approved plan by routing tasks to specialized workers.

### 3. The Agents (Workers)

Agents are categorized into two types: **Generalist** and **Specialist**.

#### A. The Generalist (Compute)

- **Logic Agent**: A "Code Interpreter" that writes and runs Python code. It handles dynamic tasks like complex math, data transformation, or unforeseen problems.

#### B. The Specialists (Reliability)

Hardcoded specialist agents are used for interacting with the outside world to ensure **reliability** and **safety** (avoiding broken scrapers or mishandled secrets).

- **Market Agent**: Fetches real-time OHLC data using `yfinance`.
- **Research Agent**: Retrieves recent news and context using `duckduckgo-search`.
- **Chart Agent**: Generates interactive visualization using `plotly`.
- **Email Agent**: Formats and dispatches (mocks) the final intelligence report.

> **Why split them?**
> A Logic agent _could_ try to scrape the web to find stock prices, but it might get blocked or crash. By using a specialized **Market Agent**, reliable access to data is guaranteed, while leaving the **Logic Agent** free to do the difficult math on that data.

_Note: The architecture is designed to be extensible. To add a new capability (e.g., "Calendar Management"), simply add a new Agent+Tool pair and register it with the Supervisor._

## Technology Stack

- **Python & LangGraph**: For stateful, cyclic agent orchestration.
- **Groq (Llama 3)**: For high-speed, low-latency inference.
- **Chainlit**: For a "Thinking Process" UI that visualizes the agent's internal state.
