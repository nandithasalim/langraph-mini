nodes = {}
edges = {}
conditional_edges = {}
import json,os

class FileCheckpointer:
    def __init__(self, filepath):
        self.filepath = filepath
    
    def save(self, state, next_node):
        checkpoint = {"state": state, "next_node": next_node}
        with open(self.filepath, "w") as f:
            json.dump(checkpoint, f)
    
    def load(self):
        try:
            with open(self.filepath) as f:
                return json.load(f)   # returns {"state": ..., "next_node": ...}
        except FileNotFoundError:
            return None
        
def add_node(name, function):
    nodes[name] = function

def add_edge(func1, func2):
    if func1 not in nodes or func2 not in nodes:
        raise ValueError("One or both functions are not added as nodes.")
    edges[func1] = func2

entry_point = None
def set_entry(node_name):
    global entry_point
    entry_point = node_name
reducers={}
def register_reducer(key, reducer_function):
    reducers[key] = reducer_function

def append_reducer(old, new):
    if old is None:
        return new
    return old + new
def add_conditional_edge(from_node, decision_function):
    conditional_edges[from_node] = decision_function

def stream(initial_state=None,max_iterations=100,checkpointer=None):
    current=entry_point
    if checkpointer:
        saved = checkpointer.load()
        if saved:
            state = saved["state"]
            current=saved["next_node"]
        else:
            state = initial_state or {}
    else:
        state = initial_state or {}
    iterations = 0
    while current :
        if iterations >= max_iterations:
            raise RuntimeError(
            f"Graph exceeded max iterations ({max_iterations}). "
            f"Possible infinite loop. Last node: '{current}'"
        )
        update = nodes[current](state)
        for key, new_value in update.items():
            if key in reducers:
                # use the reducer to merge
                old_value = state.get(key)
                state[key] = reducers[key](old_value, new_value)
            else:
                # no reducer, just overwrite like before
                state[key] = new_value

        if current in edges:
            current = edges[current]
        elif current in conditional_edges:
            decision_function = conditional_edges[current]
            current = decision_function(state)
        else:
            current = None
        if checkpointer:
            checkpointer.save(state, current)
        yield dict(state)
        iterations += 1
    
def run(initial_state=None, max_iterations=100,checkpointer=None):
    # just consume stream and return the last state
    final = None
    for state in stream(initial_state, max_iterations,checkpointer):
        final = state
    return final
        


# clean slate
if os.path.exists("state.json"):
    os.remove("state.json")

nodes.clear()
edges.clear()

def step1(state):
    print("→ step1 running")
    return {"step1_done": True}

def step2(state):
    print("→ step2 running")
    return {"step2_done": True}

def step3(state):
    print("→ step3 CRASHING")
    raise RuntimeError("boom")

def step4(state):
    print("→ step4 running")
    return {"step4_done": True}

add_node("step1", step1)
add_node("step2", step2)
add_node("step3", step3)
add_node("step4", step4)
add_edge("step1", "step2")
add_edge("step2", "step3")
add_edge("step3", "step4")
set_entry("step1")

cp = FileCheckpointer("state.json")

# First run — crashes at step3
print("=== First run ===")
try:
    run(checkpointer=cp)
except RuntimeError as e:
    print(f"Crashed: {e}")

print(f"\nCheckpoint after crash: {cp.load()}\n")

# Fix step3 and resume
def step3_fixed(state):
    print("→ step3 (fixed) running")
    return {"step3_done": True}

nodes["step3"] = step3_fixed

print("=== Resume ===")
result = run(checkpointer=cp)
print(f"\nFinal: {result}")
