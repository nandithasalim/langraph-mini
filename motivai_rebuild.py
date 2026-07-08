from main import (
    add_node, add_edge, set_entry, run,
    nodes, edges, conditional_edges, reducers
)

# clear any state from earlier tests
nodes.clear()
edges.clear()
conditional_edges.clear()
reducers.clear()


# Node 1: retrieve past completed tasks (stubbed) 
def retrieve_context(state):
    print(f"[retrieve_context] fetching past tasks for user {state['user_id']}")
    # In real MotivAI: does a pgvector cosine search against user's completed tasks.
    # Here: return fake past tasks.
    past_tasks = [
        {"description": "20 min run"},
        {"description": "HIIT workout"},
        {"description": "study Python"},
    ]
    return {"past_tasks": past_tasks}


# Node 2: generate motivational reaction (stubbed) 
def generate_reaction(state):
    print(f"[generate_reaction] generating reaction for: '{state['description']}'")
    # In real MotivAI: model routing (gpt-4o vs 4o-mini based on streak),
    # semantic cache check, fallback chain, content filter.
    # Here: return fake reaction.
    past = ", ".join(t["description"] for t in state["past_tasks"])
    reaction = {
        "message": f"Nice work on '{state['description']}'! You've been consistent — {past}",
        "emoji": "💪",
        "streak_count": 7,
        "tone": "motivational",
    }
    return {"reaction": reaction}


# Node 3: store reaction in group_posts (stubbed) 
def store_reaction(state):
    print(f"[store_reaction] saving reaction to group {state.get('group_id')}")
    # In real MotivAI: UPDATE group_posts SET agent_reaction = ...,
    # then invalidate Redis feed cache.
    # Here: just mark as stored.
    return {"stored": True}


#  Wire the graph up 
add_node("retrieve_context", retrieve_context)
add_node("generate_reaction", generate_reaction)
add_node("store_reaction", store_reaction)

add_edge("retrieve_context", "generate_reaction")
add_edge("generate_reaction", "store_reaction")

set_entry("retrieve_context")


# Run it, same way you'd invoke the real agent 
if __name__ == "__main__":
    initial_state = {
        "user_id": "user_42",
        "task_id": "task_123",
        "description": "finished 30 min meditation",
        "group_id": "group_7",
    }
    
    print("=== Running MotivAI pipeline on minigraph ===\n")
    final_state = run(initial_state)
    print("\n=== Final state ===")
    for key, value in final_state.items():
        print(f"  {key}: {value}")

add_node("retrieve_context", retrieve_context)
add_node("generate_reaction", generate_reaction)
add_node("store_reaction", store_reaction)
set_entry("retrieve_context")
add_edge("retrieve_context", "generate_reaction")
add_edge("generate_reaction", "store_reaction")