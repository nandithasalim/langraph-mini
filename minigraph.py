nodes = {}
edges = {}
conditional_edges = {}
entry_point = None  # name of first node to execute
import json,os

class FileCheckpointer:
    """
    Stores both the current state AND which node is scheduled to run next,
    so a graph can resume mid-execution after a crash without re-running
    nodes that already completed.

    Real LangGraph supports multiple backends (SQLite, Postgres, Redis).
    This is the simplest one — file-based JSON.
    """
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


def set_entry(node_name):
    global entry_point
    entry_point = node_name

reducers={}
def register_reducer(key, reducer_function):
    """
    Without a registered reducer, the default behavior is 'overwrite'
    (new value replaces old). With a reducer, the framework calls
    reducer_function(old_value, new_value) and stores the result.
    """
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
        update = nodes[current](state) #run current node

        for key, new_value in update.items():
            if key in reducers:
                # use the reducer to merge
                old_value = state.get(key)
                state[key] = reducers[key](old_value, new_value)
            else:
                # no reducer, just overwrite like before
                state[key] = new_value

        #Decide the next node
        if current in edges:
            current = edges[current]
        elif current in conditional_edges:
            decision_function = conditional_edges[current]
            current = decision_function(state)
        else:
            current = None
        #Save checkpoint AFTER we know the next node, so resume works
        if checkpointer:
            checkpointer.save(state, current)
        yield dict(state) # give live reference
        iterations += 1
    
def run(initial_state=None, max_iterations=100,checkpointer=None):
    # just consume stream and return the last state
    final = None
    for state in stream(initial_state, max_iterations,checkpointer):
        final = state
    return final
        
