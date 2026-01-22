import chainlit as cl
from agents.graph import graph
import plotly.graph_objects as go

@cl.on_chat_start
async def start():
    """Initialize the chat session"""
    await cl.Message(
        content="👋 **Welcome to Multi-Agent Financial Analyst!**\n\nI can help you with:\n- Stock/crypto analysis\n- Market research\n- Financial calculations\n- News and trends\n\nWhat would you like to explore?",
    ).send()
    
    cl.user_session.set("chat_history", [])


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages with streaming and collapsible steps"""
    chat_history = cl.user_session.get("chat_history")
    chat_history.append({"role": "user", "content": message.content})
    
    initial_state = {
        "messages": chat_history,
        "plan": [],
        "is_ambiguous": False,
        "clarifying_question": "",
        "final_report": ""
    }
    
    # Main thinking step
    async with cl.Step(name="Planning", type="run") as planning_step:
        final_state = None
        plan = None
        
        try:
            for event in graph.stream(initial_state):
                for key, value in event.items():
                    
                    if key == 'planner':
                        if value.get('is_ambiguous'):
                            # Clarifying question
                            response = value.get('clarifying_question', '')
                            planning_step.output = f"Need clarification"
                            
                            await cl.Message(content=response).send()
                            chat_history.append({"role": "assistant", "content": response})
                            cl.user_session.set("chat_history", chat_history)
                            return
                        else:
                            # Plan created
                            plan = value.get('plan', [])
                            plan_text = "\n".join([f"{i}. {step}" for i, step in enumerate(plan, 1)])
                            planning_step.output = plan_text
                    
                    final_state = value
        
        except Exception as e:
            planning_step.output = f"Error: {e}"
            await cl.Message(content=f"❌ **Error in planning:** {str(e)}").send()
            return
    
    # Execution step (collapsible)
    if plan:
        async with cl.Step(name=f"Executing {len(plan)} steps", type="tool") as execution_step:
            execution_step.output = "Running tools..."
            
            # Wait for supervisor to finish
            # (The graph already executed above, we're just showing status here)
    
    # Stream the final response
    if final_state and "final_report" in final_state:
        response = final_state["final_report"]
        
        # Check for any Plotly figures in the state
        # (We'll need to modify supervisor to store these)
        
        # Stream the response token by token
        msg = cl.Message(content="")
        await msg.send()
        
        for token in response.split():
            await msg.stream_token(token + " ")
        
        await msg.update()
        
        chat_history.append({"role": "assistant", "content": response})
        cl.user_session.set("chat_history", chat_history)
    else:
        await cl.Message(content="✅ Task completed.").send()
