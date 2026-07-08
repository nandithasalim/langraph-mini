nodes = {}
edges = {}

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

def run():
    state = {}
    current=entry_point
    while current:
        update = nodes[current](state)
        for key, new_value in update.items():
            if key in reducers:
                # use the reducer to merge
                old_value = state.get(key)
                state[key] = reducers[key](old_value, new_value)
            else:
                # no reducer, just overwrite like before
                state[key] = new_value
        current = edges.get(current)
    return state
        
