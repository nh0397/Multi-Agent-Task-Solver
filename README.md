# Multi-Agent Financial Analyst

A state-aware multi-agent system designed to act as a competent financial analyst. It interprets natural language requests, plans execution strategies, and orchestrates specialized tools to deliver comprehensive market analysis.

## Architecture & Design

### System Overview

![Architecture Diagram](architecture_diagram_1769103579280.png)

### Design Decisions & Trade-offs

During the development of this system, several architectural trade-offs were considered to balance performance, cost, and reliability.

#### 1. Planner-Supervisor Pattern vs. Single Loop (ReAct)

- **Decision**: A two-step **Planner-Supervisor** pattern was adopted.
- **Rationale**: A single "ReAct" loop often rushes to execution. For example, if a user asks "How is the market?", a simple agent might randomly pick a stock. A **Planner** acts as a firewall, detecting ambiguity (e.g., "Which market?") and asking clarifying questions before any tools are invoked. This ensures safety and precision.

#### 2. LLM Provider (Groq) & Model Selection

- **Decision**: **Groq** is utilized for interference to ensure low latency.
- **Model Strategy**: The system is designed to switch between models based on rate limits and availability.
  - **Mixtral 8x7b**: Used for high-speed routing.
  - **Llama 3 70B**: Used for complex reasoning.
  - **GPT-OSS-120B**: Currently selected for enhanced synthesis capabilities.
- **Trade-off**: While OpenAI (GPT-4) offers marginally higher reasoning capabilities, the latency introduced by external API calls disrupts the real-time "agentic" feel. Groq's sub-second inference speeds were prioritized to maintain a responsive user experience.

#### 3. Chainlit vs. Streamlit/Next.js

- **Decision**: The UI is built with **Chainlit**.
- **Rationale**:
  - _Next.js_ was considered too complex for a rapid Python-based agent prototype.
  - _Streamlit_ refreshes the entire page on interaction, breaking the conversational flow.
  - _Chainlit_ is built specifically for LLM apps, providing native streaming, "Step" expansion, and persistent chat sessions out of the box.

#### 4. Specialized Agents vs. Generalist

- **Decision**: Dedicated tools were implemented for Market, Search, and Email.
- **Rationale**: Generalist LLMs can hallucinate data. Hard-coded tools (using `yfinance` for prices, `smtplib` for email) provide deterministic guarantees. The LLM's role is restricted to _orchestration_ and _synthesis_, not data generation.

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
GROQ_API_KEY=your_key_here

# Optional (for Email features)
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
```

_Note: If using Gmail, an [App Password](https://myaccount.google.com/apppasswords) is required._

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
