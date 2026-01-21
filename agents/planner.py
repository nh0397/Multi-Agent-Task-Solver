from langchain_core.prompts import ChatPromptTemplate
from agents.llm import get_llm
from agents.state import AgentState
import json

# 1. The prompt that forces JSON output
PLANNER_PROMPT = """You are a Financial Intelligence Planner.
Your job is to check if the user's request is clear enough to execute.

User Request: {input}

RULES:
1. If the request is VAGUE (e.g. "How is the stock?", "What's the news?", "Analyze the company"), output JSON:
   {{
     "is_ambiguous": true,
     "clarifying_question": "Which specific company or ticker are you referring to?"
   }}

2. If the request is CLEAR (e.g. "Analyze NVDA", "Why is TSLA down?"), output JSON:
   {{
     "is_ambiguous": false,
     "plan": [
        "Step 1: Fetch stock data for...",
        "Step 2: Search for news about...",
        "Step 3: Generate a chart...",
        "Step 4: Email a summary..."
     ]
   }}
   
Make the plan steps EXPLICIT and actionable.
Output ONLY valid JSON.
"""

def planner_node(state: AgentState):
    """
    The Planner Node. Checks ambiguity and generates a plan.
    """
    # 1. Get the latest user message
    messages = state['messages']
    user_input = messages[-1]['content']
    
    # 2. Prepare the chain
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template(PLANNER_PROMPT)
    chain = prompt | llm
    
    try:
        # 3. Call the LLM
        response = chain.invoke({"input": user_input})
        
        # 4. Clean and Parse JSON
        content = response.content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)
        
        # 5. Return updates to the state
        return {
            "is_ambiguous": data.get("is_ambiguous", False),
            "clarifying_question": data.get("clarifying_question", ""),
            "plan": data.get("plan", [])
        }
        
    except Exception as e:
        # Fallback if JSON parsing fails
        return {
            "is_ambiguous": True,
            "clarifying_question": f"I had trouble listing the plan. Could you rephrase request?"
        }
