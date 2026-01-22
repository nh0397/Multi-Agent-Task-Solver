from agents.state import AgentState
from agents.llm import get_llm
from tools.market import get_stock_prices
from tools.search import search_web
from tools.chart import generate_chart, generate_comparison_chart
from tools.email import send_email
import re
import json

def supervisor_node(state: AgentState):
    """
    Intelligent supervisor that routes plan steps to the right tools using LLM.
    """
    plan = state['plan']
    
    if not plan:
        return {"final_report": "No plan to execute.", "charts": [], "sources": []}
    
    results = []
    results = []
    
    # Load persistent context
    context_data = state.get('context_data', {'market_data': {}, 'chart_paths': []})
    market_data = context_data.get('market_data', {})
    chart_paths = context_data.get('chart_paths', [])
    
    charts = []  # Store new Plotly figures for UI display
    sources = []  # Store search sources for citation
    
    for i, step in enumerate(plan, 1):
        print(f"\n[SUPERVISOR] Step {i}/{len(plan)}: {step}")
        
        # Ask LLM which tool to use
        tool_choice = decide_tool(step)
        tool_name = tool_choice['tool'].lower().strip()
        print(f"[SUPERVISOR] Routing to: {tool_name}")
        
        step_result = f"### Step {i}: {step}\n\n"
        
        try:
            if tool_name == 'market':
                raw_ticker = tool_choice['params'].get('ticker', extract_ticker(step))
                # Support multiple tickers comma-separated
                tickers = [t.strip() for t in raw_ticker.split(',')]
                
                for ticker in tickers:
                    if ticker and ticker not in market_data:
                        result = get_stock_prices(ticker)
                        if result['error']:
                            step_result += f"Error fetching {ticker}: {result['message']}\n"
                        else:
                            market_data[ticker] = result['csv']  # Store pure CSV
                            step_result += f"Fetched {len(result['csv'].splitlines())} rows for {ticker}\n"
                            
                            # Add data excerpt for LLM synthesis (First 5 and Last 5 rows)
                            lines = result['csv'].splitlines()
                            excerpt = "\n".join(lines[:6]) + "\n...\n" + "\n".join(lines[-5:]) if len(lines) > 10 else result['csv']
                            
                            results.append(f"Market Data for {ticker}:\n{excerpt}")
                    elif ticker:
                        step_result += f"Using cached data for {ticker}\n"
            
            elif tool_name == 'search':
                query = tool_choice['params'].get('query', step)
                result = search_web(query)
                step_result += result['content']
                sources.extend(result['sources'])  # Collect sources
            
            elif tool_name == 'chart':
                ticker = tool_choice['params'].get('ticker', extract_ticker(step))
                # Check if this is a comparison request (multiple tickers in market_data)
                if len(market_data) > 1:
                    # Generate comparison chart with all tickers
                    fig = generate_comparison_chart(market_data)
                    if isinstance(fig, str):
                        print(f"[CHART ERROR] {fig}")
                        step_result += f"Chart generation skipped"
                    else:
                        if fig not in charts:  # Avoid duplicate charts
                            charts.append(fig)
                            # Save persistent image
                            try:
                                path = f"/tmp/chart_comparison_{len(chart_paths)}.png"
                                fig.write_image(path)
                                chart_paths.append(path)
                            except Exception as e:
                                print(f"Failed to save chart image: {e}")
                        step_result += f"Comparison chart generated for {', '.join(market_data.keys())}"
                elif ticker and ticker in market_data:
                    fig = generate_chart(ticker, market_data[ticker])
                    if isinstance(fig, str):
                        print(f"[CHART ERROR] {fig}")
                        step_result += f"Chart generation skipped for {ticker}"
                    else:
                        charts.append(fig)
                        # Save persistent image
                        try:
                            path = f"/tmp/chart_{ticker}_{len(chart_paths)}.png"
                            fig.write_image(path)
                            chart_paths.append(path)
                        except Exception as e:
                            print(f"Failed to save chart image: {e}")
                        step_result += f"Chart generated for {ticker}"
                else:
                    step_result += f"Note: Chart skipped - no market data for {ticker}"
            
            elif tool_name == 'email':
                from tools.email import format_report_html
                import os
                
                # Default to user's configured email ONLY if explicitly requested as "my email"
                # Otherwise, if recipient is missing or generic, we should have caught this in planner
                recipient = tool_choice['params'].get('recipient', '')
                
                # Regex Fallback: If LLM failed to extract email but it's in the step description
                if not recipient or '@' not in recipient:
                    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', step)
                    if match:
                        recipient = match.group(0)
                        print(f"[SUPERVISOR] Recovered recipient from step text: {recipient}")
                
                if not recipient or recipient == 'user@example.com':
                     step_result += "Error: No recipient email provided. Please specify an email address."
                     results.append(step_result)
                     continue
                
                # Generate smart email body using LLM
                # Use FULL conversation history for context
                history_text = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in state['messages']])
                
                email_prompt = f"""You are a professional financial assistant drafting an email report.
                
CONTEXT from conversation history:
{history_text}

NEW FINDINGS from current tool execution:
{chr(10).join(results)}

TASK:
Write a comprehensive email body.
- If the user asked to "send this", refer to the entire context of what was discussed.
- Summarize the key insights from the conversation (stocks analyzed, trends found).
- Mention that charts and data are attached.
- Be professional and concise."""

                subject = tool_choice['params'].get('subject', 'Financial Analysis Report')
                
                # If subject is generic, try to make it dynamic from history
                if subject == 'Financial Analysis Report':
                    try:
                        subject_prompt = f"Generate a short email subject (max 5 words) based on this conversation:\n{company_names if 'company_names' in locals() else history_text[:500]}\n\nSubject:"
                        subject_response = llm.invoke([{"role": "user", "content": subject_prompt}])
                        dynamic_subject = subject_response.content.strip().strip('"').strip("'")
                        subject = f"Multi-Agent Task Solver | {dynamic_subject}"
                    except:
                        pass # Keep default
                
                try:
                    email_body_response = llm.invoke([{"role": "user", "content": email_prompt}])
                    email_body_text = email_body_response.content
                except:
                    email_body_text = "Here is the report based on our conversation."

                # Format report as HTML
                html_body = format_report_html(
                    title=subject,
                    content=email_body_text,
                    sources=sources if sources else None
                )
                
                # Attachments: ALL Charts (accumulated) + ALL Data (accumulated)
                email_attachments = []
                
                # 1. Accumulated Charts
                email_attachments.extend(chart_paths)
                
                # 2. Accumulated CSV Data
                for ticker, csv_content in market_data.items():
                    csv_path = f"/tmp/{ticker}_data.csv"
                    with open(csv_path, 'w') as f:
                        f.write(csv_content)
                    email_attachments.append(csv_path)
                
                # Send email with attachments
                print(f"[EMAIL] Sending to {recipient} with {len(email_attachments)} attachments...")
                result = send_email(recipient, subject, html_body, attachments=email_attachments if email_attachments else None)
                print(f"[EMAIL] Result: {result}")
                step_result += result
            
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
    
    # Check if this is a chart-only request (no text needed)
    chart_only = len(charts) > 0 and len(results) <= len(charts)
    
    if chart_only:
        # User only wants charts, skip text synthesis
        final_report = ""
    else:
        # Generate text summary
        llm = get_llm()
        # Truncate results to avoid token limits
        results_text = "\n".join(results)
        if len(results_text) > 12000:
            results_text = results_text[:12000] + "... (truncated)"

        synthesis_prompt = f"""You are a smart financial assistant.
The user asked a question and we ran some tools to get data.
Here is the raw data collected:

{results_text}

YOUR TASK:
Synthesize this into a direct, human-like answer.
- IGNORE tool log messages like "Fetched 20 rows" or "Using cached data".
- Focus on the *actual values* (prices, dates, news headlines).
- If asked about a trend, describe the trend (up/down/volatility) using the data.
- Do not meta-explain ("Based on the data...", "The tools found..."). Just answer.
- Be concise but professional."""

        try:
            synthesis_response = llm.invoke([{"role": "user", "content": synthesis_prompt}])
            final_report = synthesis_response.content
        except Exception as e:
            print(f"[SYNTHESIS ERROR] {e}")
            # Retry with shorter prompt if first fails
            try:
                short_prompt = f"Summarize this data briefly: {results_text[:4000]}"
                response = llm.invoke([{"role": "user", "content": short_prompt}])
                final_report = response.content
            except:
                final_report = "I gathered the data but couldn't generate a summary. Please check the logs."
    
    # Check for email confirmation in results and append to final report if not present
    email_confirmations = [r for r in results if "Email sent to" in r]
    if email_confirmations:
        for confirmation in email_confirmations:
            # Extract just the relevant line
            lines = confirmation.split('\n')
            for line in lines:
                if "Email sent to" in line:
                    final_report += f"\n\n✅ {line}"
    
    return {
        "final_report": final_report, 
        "charts": charts, 
        "sources": sources,
        "context_data": {
            "market_data": market_data,
            "chart_paths": chart_paths
        }
    }


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
