from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.planner import planner_node
from agents.supervisor import supervisor_node

def check_ambiguity(state: AgentState):
    """
    Conditional logic to determine the next step after Planner.
    """
    if state.get('is_ambiguous'):
        return "ask_user"
    return "execute"

# 1. Initialize the Graph
workflow = StateGraph(AgentState)

# 2. Add Nodes
workflow.add_node("planner", planner_node)
workflow.add_node("supervisor", supervisor_node)

# 3. Define Entry Point
workflow.set_entry_point("planner")

# 4. Define Edges
# From Planner, we split:
# - If ambiguous -> END (We need to ask the user)
# - If clear -> Go to Supervisor
workflow.add_conditional_edges(
    "planner",
    check_ambiguity,
    {
        "ask_user": END,
        "execute": "supervisor"
    }
)

# From Supervisor, we end (Task complete)
workflow.add_edge("supervisor", END)

# 5. Compile the Graph
graph = workflow.compile()
