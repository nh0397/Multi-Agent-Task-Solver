from agents.state import AgentState
from tools.market import get_stock_prices
from tools.search import search_web
from tools.chart import generate_chart
from tools.email import send_email
import re

def supervisor_node(state: AgentState):
    """
    Supervisor Node.
    Iterates through the plan and executes tools based on keywords.
    """
    plan = state['plan']
    results = []
    context = "" # Accumulates data for the final report
    
    if not plan:
        return {"final_report": "I have no plan to execute."}

    for step in plan:
        step_lower = step.lower()
        step_output = f"--- Executing: {step} ---\n"
        
        # 1. EXTRACT TICKER (Simple Regex heuristic)
        # Looks for 2-5 uppercase letters (e.g., NVDA, AAPL)
        ticker_match = re.search(r'\b[A-Z]{2,5}\b', step) 
        ticker = ticker_match.group(0) if ticker_match else None
        
        # 2. ROUTE TO TOOLS
        
        # MARKET TOOL
        if "fetch" in step_lower or "price" in step_lower or "stock" in step_lower:
            if ticker:
                step_output += get_stock_prices(ticker=ticker)
            else:
                step_output += "Error: Could not identify a ticker for market data."

        # SEARCH TOOL
        elif "news" in step_lower or "search" in step_lower or "why" in step_lower:
            step_output += search_web(query=step)

        # CHART TOOL
        elif "chart" in step_lower or "graph" in step_lower or "plot" in step_lower:
            if ticker:
                # We assume 'context' contains the CSV data from a previous step
                # In a real system, we'd pass the specific artifact ID
                # Here we just pass the raw context and let the tool try to parse it
                chart_fig = generate_chart(ticker=ticker, data_csv=context)
                if isinstance(chart_fig, str): # Error message
                    step_output += chart_fig
                else:
                    # In Chainlit, we can't store the Figure object in the text context.
                    # We will append a placeholder and handle the UI rendering in app.py
                    # OR we can save it to state if we expand State to hold objects.
                    # For now, let's signal success.
                    step_output += f"Chart generated for {ticker}."
            else:
                step_output += "Error: No ticker logic for chart."

        # EMAIL TOOL
        elif "email" in step_lower or "send" in step_lower:
            step_output += send_email(recipient="user@example.com", subject=f"Report: {ticker}", body=context[:1000])

        else:
            step_output += "(Step requires manual logic or is informational)"

        results.append(step_output)
        context += step_output + "\n\n"
        
    return {"final_report": context}
