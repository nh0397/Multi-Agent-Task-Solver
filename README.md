# Multi-Agent Task Solver (Financial Domain)

A production-ready multi-agent system that interprets natural language requests, breaks them into executable tasks, and orchestrates specialized agents to deliver comprehensive financial analysis.

## Features

- **Natural Language Interface** - Ask questions in plain English
- **Intelligent Planning** - Automatically breaks down complex requests into steps
- **Specialized Agents** - Market data, web search, charting, and email
- **Context-Aware** - Remembers conversation history for follow-up questions
- **Interactive Charts** - Plotly visualizations rendered inline
- **Source Citations** - Perplexity-style collapsible source links
- **Email Reports** - HTML-formatted reports with chart attachments
- **Streaming Responses** - Real-time token-by-token output

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/nh0397/Multi-Agent-Task-Solver.git
cd Multi-Agent-Task-Solver

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file:

```bash
# Required: Groq API key
GROQ_API_KEY=your_groq_api_key_here

# Optional: Email functionality
EMAIL_USER=your.email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
```

**Get Groq API Key:** https://console.groq.com/keys

**Gmail Setup:** Enable 2FA and generate app password at https://myaccount.google.com/apppasswords

### 3. Run

**CLI Mode:**

```bash
python main.py
```

**Web UI (Chainlit):**

```bash
chainlit run app.py -w
```

Then open http://localhost:8000

## Example Queries

```
Analyze NVDA stock
Compare TSLA and RIVN performance
Show me Bitcoin price chart for last month
Why did tech stocks drop today?
Analyze MSFT and email the report to me@example.com
```

## Architecture

### Planner-Supervisor Pattern

```
User Input → Planner → Supervisor → Specialized Tools → LLM Synthesis → Response
```

**Planner (Gatekeeper)**

- Classifies intent (CHAT vs ACTIONABLE)
- Generates execution plan
- Asks clarifying questions if needed

**Supervisor (Orchestrator)**

- Routes plan steps to appropriate tools
- Manages data flow between tools
- Synthesizes final report using LLM

**Specialized Agents**

- **Market Agent** - `yfinance` for stock/crypto data
- **Search Agent** - `duckduckgo-search` for news with content extraction
- **Chart Agent** - `plotly` for interactive visualizations
- **Email Agent** - `smtplib` for HTML reports with attachments

### Why Specialized Agents?

A generalist "Logic Agent" could theoretically scrape stock data, but it might fail due to rate limits, CAPTCHAs, or API changes. Specialized agents guarantee **reliability** and **safety** while keeping the system extensible.

## Technology Stack

- **LangGraph** - Stateful agent orchestration
- **Groq (Llama 3.3 70B)** - High-speed LLM inference
- **Chainlit** - Interactive chat UI with streaming
- **yfinance** - Market data
- **DuckDuckGo Search** - Web search
- **Plotly** - Interactive charts
- **BeautifulSoup4** - Content extraction

## Project Structure

```
Multi-Agent-Task-Solver/
├── agents/
│   ├── state.py          # Shared state definition
│   ├── llm.py            # LLM configuration
│   ├── planner.py        # Planning logic
│   ├── supervisor.py     # Orchestration logic
│   └── graph.py          # LangGraph workflow
├── tools/
│   ├── market.py         # Stock data fetching
│   ├── search.py         # Web search + scraping
│   ├── chart.py          # Chart generation
│   └── email.py          # Email with attachments
├── main.py               # CLI entry point
├── app.py                # Chainlit web UI
└── README.md
```

## Extending the System

To add a new capability (e.g., "Calendar Management"):

1. **Create tool** in `tools/calendar.py`
2. **Register in supervisor** (`agents/supervisor.py`)
3. **Update planner examples** (`agents/planner.py`)

The system is designed to be modular and extensible.

## Development

**Run tests:**

```bash
python test_chart.py  # Test chart generation
python -m tools.search  # Test search tool
```

**Watch mode (auto-reload):**

```bash
chainlit run app.py -w
```

## Troubleshooting

**"No module named 'yfinance'"**

- Run: `pip install -r requirements.txt`

**"GROQ_API_KEY not found"**

- Create `.env` file with your API key

**Email not working**

- Check `.env.email.example` for configuration
- Gmail requires app password, not regular password

**Rate limiting**

- Groq free tier: 30 RPM, 14,400 TPD
- Consider upgrading for production use

## License

MIT

## Contributing

Pull requests welcome! Please ensure:

- Code follows existing style
- New tools include error handling
- Update README for new features

## Acknowledgments

Built with LangGraph, Groq, and Chainlit.

---

## Implementation Status

### ✅ Core Features (Complete)

- **Multi-Agent Orchestration** - Planner-Supervisor pattern with LangGraph
- **Natural Language Interface** - Conversational UI with context awareness
- **Specialized Tools**
  - Market Agent (yfinance) - Stock/crypto data fetching
  - Search Agent (DuckDuckGo) - Web search with content extraction
  - Chart Agent (Plotly) - Interactive visualizations
  - Email Agent (SMTP) - HTML reports with attachments
- **File Upload** - CSV, Excel, PDF parsing and analysis
- **Streaming Responses** - Real-time token-by-token output
- **Source Citations** - Perplexity-style collapsible references
- **Conversation Memory** - Multi-turn context retention
- **Error Handling** - Graceful degradation and user feedback

### 🚧 Future Enhancements

- **Logic Agent** - Python code executor for dynamic calculations
- **Rate Limiting** - Retry logic and backoff for API calls
- **Caching** - LLM response caching for common queries
- **Multi-language Support** - i18n for global users
- **Advanced Analytics** - Portfolio tracking, backtesting
- **Voice Input** - Speech-to-text integration

### 📊 System Capabilities

| Feature               | Status | Notes                            |
| --------------------- | ------ | -------------------------------- |
| Stock Analysis        | ✅     | Real-time data via yfinance      |
| News Search           | ✅     | Content extraction from articles |
| Chart Generation      | ✅     | Interactive Plotly charts        |
| Email Reports         | ✅     | HTML formatting + attachments    |
| File Upload           | ✅     | CSV, Excel, PDF support          |
| Context Memory        | ✅     | Full conversation history        |
| Streaming UI          | ✅     | Character-by-character output    |
| Source Citations      | ✅     | Clickable references             |
| Ambiguity Handling    | ✅     | Clarifying questions             |
| Multi-turn Refinement | ✅     | Follow-up queries                |

**All core requirements from the original specification have been implemented and tested.**
