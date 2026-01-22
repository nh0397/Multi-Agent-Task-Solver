from agents.state import AgentState
from agents.llm import get_llm
from tools.market import get_stock_prices
from tools.search import search_web
from tools.chart import generate_chart
from tools.email import send_email
import re
import json

def supervisor_node(state: AgentState):
    """
    Intelligent supervisor that routes plan steps to the right tools using LLM.
    """
    plan = state['plan']
    
    if not plan:
        return {"final_report": "No plan to execute."}
    
    results = []
    market_data = {}  # Store fetched data by ticker
    
    for i, step in enumerate(plan, 1):
        print(f"\n[SUPERVISOR] Step {i}/{len(plan)}: {step}")
        
        # Ask LLM which tool to use
        tool_choice = decide_tool(step)
        print(f"[SUPERVISOR] Routing to: {tool_choice['tool']}")
        
        step_result = f"### Step {i}: {step}\n\n"
        
        try:
            if tool_choice['tool'] == 'market':
                ticker = tool_choice['params'].get('ticker', extract_ticker(step))
                if ticker:
                    # Only fetch if we don't have it already
                    if ticker not in market_data:
                        result = get_stock_prices(ticker)
                        if result['error']:
                            step_result += result['message']
                        else:
                            market_data[ticker] = result['csv']  # Store pure CSV
                            step_result += f"{result['message']}\n\n{result['csv']}"
                    else:
                        step_result += f"Using existing market data for {ticker}"
                else:
                    step_result += "Error: No ticker found"
            
            elif tool_choice['tool'] == 'search':
                query = tool_choice['params'].get('query', step)
                step_result += search_web(query)
            
            elif tool_choice['tool'] == 'chart':
                ticker = tool_choice['params'].get('ticker', extract_ticker(step))
                if ticker and ticker in market_data:
                    fig = generate_chart(ticker, market_data[ticker])
                    if isinstance(fig, str):
                        # Chart errored - don't include in synthesis
                        print(f"[CHART ERROR] {fig}")
                        step_result += f"Chart generation skipped for {ticker}"
                    else:
                        step_result += f"✓ Interactive chart generated for {ticker}\n(Chart will render in UI)"
                else:
                    step_result += f"Note: Chart skipped - no market data for {ticker}"
            
            elif tool_choice['tool'] == 'email':
                recipient = tool_choice['params'].get('recipient', 'user@example.com')
                subject = tool_choice['params'].get('subject', 'Financial Analysis Report')
                body = "\n\n".join(results)
                step_result += send_email(recipient, subject, body)
            
            elif tool_choice['tool'] == 'logic':
                # Python code execution would go here
                step_result += "(Logic tool not yet implemented)"
            
            else:
                step_result += "(No suitable tool found for this step)"
        
        except Exception as e:
            step_result += f"Error: {str(e)}"
        
        results.append(step_result)
    
    # FINAL SYNTHESIS: Use LLM to create a coherent natural language summary
    print("\n[SUPERVISOR] Synthesizing final report...")
    
    llm = get_llm()
    synthesis_prompt = f"""You are a financial analyst. I've gathered the following information:

{chr(10).join(results)}

Based on this data, write a clear, concise summary for the user. Include:
1. Key findings from the data
2. Important news highlights
3. Actionable insights

Write in a professional but conversational tone. Be specific with numbers."""

    try:
        synthesis_response = llm.invoke([{"role": "user", "content": synthesis_prompt}])
        final_report = synthesis_response.content
    except Exception as e:
        print(f"[SYNTHESIS ERROR] {e}")
        final_report = "\n\n".join(results)  # Fallback to raw data
    
    return {"final_report": final_report}


def decide_tool(step: str) -> dict:
    """
    Use LLM to decide which tool to use for a given step.
    """
    llm = get_llm()
    
    prompt = f"""You are a tool router. Given a task step, decide which tool to use.

AVAILABLE TOOLS:
- market: Fetch stock/crypto price data (requires ticker)
- search: Search the web for information (requires query)
- chart: Generate visualization (requires ticker)
- logic: Execute Python code for calculations
- email: Send report via email

TASK STEP: {step}

Respond with JSON:
{{
  "tool": "market|search|chart|logic|email",
  "params": {{"ticker": "NVDA", "query": "...", etc}}
}}

Output ONLY JSON."""
    
    try:
        response = llm.invoke([{"role": "user", "content": prompt}])
        content = response.content.strip()
        content = re.sub(r'```json\s*|\s*```', '', content)
        return json.loads(content)
    except:
        # Fallback to keyword matching
        step_lower = step.lower()
        if any(word in step_lower for word in ['fetch', 'price', 'data', 'stock']):
            return {"tool": "market", "params": {"ticker": extract_ticker(step)}}
        elif any(word in step_lower for word in ['search', 'news', 'why', 'research']):
            return {"tool": "search", "params": {"query": step}}
        elif any(word in step_lower for word in ['chart', 'graph', 'plot', 'visualize']):
            return {"tool": "chart", "params": {"ticker": extract_ticker(step)}}
        elif any(word in step_lower for word in ['email', 'send']):
            return {"tool": "email", "params": {}}
        else:
            return {"tool": "logic", "params": {}}


def extract_ticker(text: str) -> str:
    """Extract ticker symbol from text."""
    match = re.search(r'\b([A-Z]{2,5}(?:-[A-Z]+)?)\b', text)
    return match.group(1) if match else None
