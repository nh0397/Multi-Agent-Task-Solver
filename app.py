import chainlit as cl
from agents.graph import graph
import plotly.graph_objects as go

@cl.on_chat_start
async def start():
    """Initialize the chat session"""
    await cl.Message(
        content="""**Welcome to Multi-Agent Task Solver (Financial Domain)**

I can help you with:
- **Stock & Crypto Analysis** - Analyze price trends, volume, and performance
- **Market Research** - Search for news, trends, and expert analysis  
- **Data Visualization** - Generate interactive charts for any ticker
- **Financial Calculations** - Compute returns, ratios, and projections
- **Report Generation** - Create and email comprehensive reports

**Examples:**
- "Analyze NVDA stock"
- "Compare TSLA and RIVN"
- "Show me Bitcoin price chart"
- "Why did tech stocks drop today?"

What would you like to explore?""",
    ).send()
    
    # Initialize with empty list
    # Initialize session state
    cl.user_session.set("chat_history", [])
    cl.user_session.set("context_data", {"market_data": {}, "chart_paths": []})


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages"""
    chat_history = cl.user_session.get("chat_history") or []
    
    # Add user message
    chat_history.append({"role": "user", "content": message.content})
    cl.user_session.set("chat_history", chat_history)
    
    context_data = cl.user_session.get("context_data") or {"market_data": {}, "chart_paths": []}
    
    initial_state = {
        "messages": chat_history,
        "plan": [],
        "is_ambiguous": False,
        "clarifying_question": "",
        "final_report": "",
        "charts": [],
        "sources": [],
        "context_data": context_data
    }
    
    # Planning step (collapsible)
    async with cl.Step(name="Planning", type="run") as planning_step:
        final_state = None
        plan = None
        charts = []  # Store any charts generated
        
        try:
            for event in graph.stream(initial_state):
                for key, value in event.items():
                    
                    if key == 'planner':
                        if value.get('is_ambiguous'):
                            response = value.get('clarifying_question', '')
                            planning_step.output = "Need clarification"
                            
                            # Send clarifying question
                            await cl.Message(content=response).send()
                            chat_history.append({"role": "assistant", "content": response})
                            cl.user_session.set("chat_history", chat_history)
                            return
                        else:
                            plan = value.get('plan', [])
                            plan_text = "\n".join([f"{i}. {step}" for i, step in enumerate(plan, 1)])
                            planning_step.output = plan_text
                    
                    final_state = value
        
        except Exception as e:
            planning_step.output = f"Error: {e}"
            await cl.Message(content=f"**Error:** {str(e)}").send()
            return
    
    # Execution step (collapsible)
    if plan:
        async with cl.Step(name=f"Executing {len(plan)} steps", type="tool") as execution_step:
            step_list = "\n".join([f"- {step}" for step in plan])
            execution_step.output = f"Running:\n{step_list}"
    
    # Send final response with streaming
    if final_state and "final_report" in final_state and final_state["final_report"]:
        response = final_state["final_report"]
        
        # Stream the response
        msg = cl.Message(content="")
        await msg.send()
        
        for char in response:
            await msg.stream_token(char)
        
        await msg.update()
        
        # Display any generated charts
        if "charts" in final_state and final_state["charts"]:
            for i, fig in enumerate(final_state["charts"], 1):
                await cl.Message(
                    content="",
                    elements=[cl.Plotly(name=f"chart_{i}", figure=fig, display="inline")]
                ).send()
        
        # Display sources (like Perplexity)
        if "sources" in final_state and final_state["sources"]:
            async with cl.Step(name=f"Sources ({len(final_state['sources'])})", type="tool") as sources_step:
                sources_text = "\n\n".join([
                    f"{i}. [{src['title']}]({src['url']})" 
                    for i, src in enumerate(final_state['sources'], 1)
                ])
                sources_step.output = sources_text
        
        # Update history with actual response
        chat_history.append({"role": "assistant", "content": response})
        cl.user_session.set("chat_history", chat_history)
        
        # Persist context data (market CSVs, charts)
        if "context_data" in final_state:
            cl.user_session.set("context_data", final_state["context_data"])
    else:
        await cl.Message(content="Task completed.").send()
