# Multi-Agent Financial Analyst

A state-aware multi-agent system designed to act as a competent financial analyst. It interprets natural language requests, plans execution strategies, and orchestrates specialized tools to deliver comprehensive market analysis.

## Architecture & Design

### System Overview (Flowchart)

```mermaid
graph TD
    User([User Input]) --> Planner[Planner Agent]

    subgraph "Reasoning Phase"
        Planner -- "Ambiguous?" --> Question[Ask Clarifying Question]
        Question --> User
        Planner -- "Clear?" --> Plan[Execution Plan]
    end

    subgraph "Execution Phase (Supervisor)"
        Plan --> Supervisor[Supervisor Agent]
        Supervisor --> Router{Router}

        Router -- "Fetch Data" --> Market[Market Tool (yfinance)]
        Router -- "Research" --> Search[Search Tool (DuckDuckGo)]
        Router -- "Visualize" --> Chart[Chart Tool (Plotly)]
        Router -- "Report" --> Email[Email Tool (SMTP)]

        Market --> Context[Shared State Context]
        Search --> Context
        Chart --> Context

        Context --> Synthesis[LLM Synthesis]
    end

    Synthesis --> Output([Final Response])
```

### Design Decisions & Trade-offs

During the development of this system, several architectural trade-offs were considered to balance performance, cost, and reliability.

#### 1. Planner-Supervisor Pattern vs. Single Loop (ReAct)

- **Decision**: Adopted a two-step **Planner-Supervisor** pattern.
- **Why**: A single "ReAct" loop often rushes to execution. For example, if a user asks "How is the market?", a simple agent might randomly pick a stock. A **Planner** acts as a firewall, detecting ambiguity (e.g., "Which market?") and asking clarifying questions before any tools are invoked. This ensures safety and precision.

#### 2. Groq (Llama/Mixtral) vs. OpenAI (GPT-4)

- **Decision**: Utilized **Groq** for interference.
- **Trade-off**: OpenAI offers slightly higher reasoning capabilities (GPT-4), but at the cost of latency. Groq provides near-instant inference (300+ tokens/s).
- **Result**: The "agentic loop" feels real-time. We addressed rate limits by implementing model fallbacks (switching from Llama 70b to Mixtral/GPT-OSS when needed).

#### 3. Chainlit vs. Streamlit/Next.js

- **Decision**: Built the UI with **Chainlit**.
- **Why**:
  - _Next.js_: Too complex for a rapid Python-based agent prototype.
  - _Streamlit_: Refreshes the entire page on interaction, breaking the conversational flow.
  - _Chainlit_: Built specifically for LLM apps, providing native streaming, "Step" expansion, and persistent chat sessions out of the box.

#### 4. Specialized Agents vs. Generalist

- **Decision**: Implemented dedicated tools for Market, Search, and Email.
- **Why**: Generalist LLMs hallucinate data. Hard-coded tools (using `yfinance` for prices, `smtplib` for email) provide deterministic guarantees. The LLM's role is restricted to _orchestration_ and _synthesis_, not data generation.

---

## Installation & Setup

### Prerequisites

- Python 3.10 or higher
- Git
- A Groq API Key (Sign up at [console.groq.com](https://console.groq.com/keys))

### Step 1: Clone the Repository

```bash
git clone https://github.com/nh0397/Multi-Agent-Task-Solver.git
cd Multi-Agent-Task-Solver
```

### Step 2: Create Virtual Environment

It is recommended to use a virtual environment to manage dependencies.

```bash
python -m venv venv
# Activate the environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configuration

Create a `.env` file in the project root:

```ini
# Required
GROQ_API_KEY=your_dummy_key_here

# Optional (for Email features)
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
```

_Note: If using Gmail, you must generate an [App Password](https://myaccount.google.com/apppasswords)._

### Step 5: Run the Application

Launch the interface:

```bash
chainlit run app.py -w
```

The application will be available at `http://localhost:8000`.

---

## Features

- **Natural Language Processing**: Understands intent, context, and nuance.
- **Persistent State**: Remembers charts and data across the entire conversation session.
- **Smart Reporting**: "Send email" commands attach all session artifacts (CSVs, PNGs) and summarize the full conversation history.
- **Hybrid Search**: Combines real-time market data with web search for context.

## Contributing

1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/amazing-feature`).
3.  Commit changes (`git commit -m 'Add amazing feature'`).
4.  Push to branch (`git push origin feature/amazing-feature`).
5.  Open a Pull Request.

## License

MIT License
