from agents.graph import graph

def main():
    print("=== Multi-Agent Financial Analyst (CLI Mode) ===")
    print("Type 'quit' to exit.")
    
    # Simple history setup for the session
    chat_history = []
    
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["quit", "exit"]:
            break
            
        # Append user message to history
        chat_history.append({"role": "user", "content": user_input})
        
        # Prepare state
        initial_state = {
            "messages": chat_history,
            "plan": [],
            "is_ambiguous": False,
            "clarifying_question": "",
            "final_report": ""
        }
        
        print("\n[Thinking...]")
        
        # Stream the graph updates
        final_state = None
        for event in graph.stream(initial_state):
            for key, value in event.items():
                print(f"\n[{key.upper()}]")
                
                if key == 'planner':
                    if value.get('is_ambiguous'):
                        print(f"Question: {value.get('clarifying_question')}")
                    else:
                        plan = value.get('plan', [])
                        print(f"Plan created with {len(plan)} steps:")
                        for i, step in enumerate(plan, 1):
                            print(f"  {i}. {step}")
                        print("\nExecuting...")
                
                elif key == 'supervisor':
                    print("Execution complete.")
                
                final_state = value

        # Handle Final Output
        # Since stream returns chunks, we might need to verify the final state from the last chunk or accumulations
        # But for CLI, let's just look at the last event values or the aggregated concept.
        
        # In this simple loop, we just re-construct behavior from what happened.
        # Ideally, we should update chat_history with the response.
        
        if final_state:
            if "clarifying_question" in final_state and final_state["clarifying_question"]:
                response = final_state["clarifying_question"]
            elif "final_report" in final_state:
                response = final_state["final_report"]
            else:
                response = "Processing complete."
            
            print(f"\nAgent: {response}")
            chat_history.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
