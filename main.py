nodes = {}
edges = {}
conditional_edges = {}

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

def stream(initial_state=None,max_iterations=100):
    state = initial_state or {}
    current=entry_point
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
        yield state
        if current in edges:
            current = edges[current]
        elif current in conditional_edges:
            decision_function = conditional_edges[current]
            current = decision_function(state)
        else:
            current = None
        iterations += 1
    
def run(initial_state=None, max_iterations=100):
    # just consume stream and return the last state
    final = None
    for state in stream(initial_state, max_iterations):
        final = state
    return final
        

