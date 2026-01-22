from agents.llm import get_llm
from agents.state import AgentState
import json
import re

SYSTEM_PROMPT = """You are a Financial Intelligence Planner with access to these tools:
- Market Data: Fetch stock/crypto prices
- Web Search: Find news, analysis, trends
- Chart Generation: Create visualizations  
- Python Execution: Run calculations
- Email: Send reports

YOUR PRIMARY DIRECTIVE: **TAKE ACTION**.

If the user mentions ANY financial topic (stock, crypto, market, company), BUILD A PLAN.
Only ask questions if the request is TRULY impossible.

CLASSIFICATION:
1. CHAT - Pure small talk with NO financial content ("Hi", "Thanks", "How are you")
2. ACTIONABLE - EVERYTHING ELSE (even vague financial questions)

RESPONSE FORMAT (JSON):
{
  "intent": "CHAT|ACTIONABLE",
  "response": "message" (CHAT only),
  "plan": ["step 1", "step 2"] (ACTIONABLE only)
}

EXAMPLES:

User: "How is NVIDIA stock doing recently?"
{"intent": "ACTIONABLE", "plan": ["Fetch market data for NVDA", "Search for NVIDIA stock recent news"]}

User: "Recent news should be good" (after discussing NVIDIA)
{"intent": "ACTIONABLE", "plan": ["Search web for NVIDIA stock recent news"]}

User: "IT Market"
{"intent": "ACTIONABLE", "plan": ["Search web for IT market trends", "Search web for major IT stock performance"]}

User: "How is the market?"
{"intent": "ACTIONABLE", "plan": ["Search web for stock market today", "Search web for S&P 500 performance"]}

User: "Bitcoin"
{"intent": "ACTIONABLE", "plan": ["Fetch market data for BTC-USD", "Search for Bitcoin news"]}

User: "Calculate compound interest $10k at 5% for 10 years"
{"intent": "ACTIONABLE", "plan": ["Use Python to calculate: P=10000, r=0.05, t=10"]}

User: "Hi"
{"intent": "CHAT", "response": "Hello! I can help with stock analysis, market research, crypto, calculations, and more. What would you like to explore?"}

KEY RULES:
- Look at conversation history for context (ticker names, topics)
- If user mentioned a ticker earlier, use it
- NEVER ask "which ticker?" if it was already mentioned
- Default to action. Only greet if pure small talk.
- Be aggressive about taking action

**CRITICAL: CHART RULES**
DO NOT include chart/visualization steps UNLESS the user EXPLICITLY uses these words:
- "show", "chart", "visualize", "graph", "plot", "draw", "display visually"

If user says "Analyze NVDA" → NO CHART (just fetch data + search)
If user says "Show me NVDA" → YES CHART

Output ONLY valid JSON."""

def planner_node(state: AgentState):
    """
    Universal financial task planner with conversation context.
    """
    messages = state['messages']
    
    llm = get_llm()
    
    # Build the full conversation for context
    llm_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add conversation history
    for msg in messages:
        role = msg.get('role', 'user')
        content = msg.get('content', '')
        llm_messages.append({"role": role, "content": content})
    
    try:
        response = llm.invoke(llm_messages)
        content = response.content.strip()
        content = re.sub(r'```json\s*|\s*```', '', content).strip()
        
        print(f"\n[PLANNER] {content[:300]}...")
        
        data = json.loads(content)
        intent = data.get("intent", "ACTIONABLE")  # Default to action!
        
        if intent == "CHAT":
            return {
                "is_ambiguous": True,
                "clarifying_question": data.get("response", "Hello! How can I help?"),
                "plan": []
            }
        
        else:  # ACTIONABLE
            plan = data.get("plan", [])
            if not plan:
                # Emergency fallback - try to search for whatever they said
                last_msg = messages[-1]['content']
                plan = [f"Search web for {last_msg}"]
            
            return {
                "is_ambiguous": False,
                "clarifying_question": "",
                "plan": plan
            }
    
    except Exception as e:
        print(f"\n[PLANNER ERROR] {e}")
        return {
            "is_ambiguous": True,
            "clarifying_question": "I had trouble understanding. Could you rephrase your request?",
            "plan": []
        }
