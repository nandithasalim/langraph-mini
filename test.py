import os
from minigraph import (
    add_node, add_edge, add_conditional_edge, set_entry,
    register_reducer, append_reducer, stream, run,
    FileCheckpointer, nodes, edges, conditional_edges, reducers
)

def reset():
    """Clear globals so each test starts fresh."""
    nodes.clear()
    edges.clear()
    conditional_edges.clear()
    reducers.clear()

def test_linear_execution():
    reset()
    def a(state): return {"x": 1}
    def b(state): return {"x": state["x"] + 1}
    def c(state): return {"x": state["x"] * 10}
    
    add_node("a", a); add_node("b", b); add_node("c", c)
    add_edge("a", "b"); add_edge("b", "c")
    set_entry("a")
    
    result = run()
    assert result["x"] == 20, f"Expected 20, got {result['x']}"
    print("✓ test_linear_execution passed")


def test_reducer_appends():
    reset()
    def a(state): return {"messages": ["hi"]}
    def b(state): return {"messages": ["hello"]}
    
    add_node("a", a); add_node("b", b)
    add_edge("a", "b")
    set_entry("a")
    register_reducer("messages", append_reducer)
    
    result = run()
    assert result["messages"] == ["hi", "hello"]
    print("✓ test_reducer_appends passed")


def test_conditional_edge():
    reset()
    def start(state): return {"age": 20}
    def allow(state): return {"result": "allowed"}
    def deny(state): return {"result": "denied"}
    def route(state):
        return "allow" if state["age"] >= 18 else "deny"
    
    add_node("start", start); add_node("allow", allow); add_node("deny", deny)
    add_conditional_edge("start", route)
    set_entry("start")
    
    result = run()
    assert result["result"] == "allowed"
    print("✓ test_conditional_edge passed")


def test_max_iterations():
    reset()
    def a(state): return {"count": state.get("count", 0) + 1}
    def route(state): return "a"     # infinite loop
    
    add_node("a", a)
    add_conditional_edge("a", route)
    set_entry("a")
    
    try:
        run(max_iterations=10)
        assert False, "Should have raised RuntimeError"
    except RuntimeError:
        print("✓ test_max_iterations passed")


def test_streaming():
    reset()
    def a(state): return {"step": 1}
    def b(state): return {"step": 2}
    
    add_node("a", a); add_node("b", b)
    add_edge("a", "b")
    set_entry("a")
    
    snapshots = list(stream())
    assert len(snapshots) == 2
    assert snapshots[0]["step"] == 1
    assert snapshots[1]["step"] == 2
    print("✓ test_streaming passed")


def test_checkpoint_and_resume():
    reset()
    if os.path.exists("test_state.json"):
        os.remove("test_state.json")
    
    call_count = {"step1": 0, "step2": 0, "step3": 0}
    
    def step1(state):
        call_count["step1"] += 1
        return {"s1": True}
    def step2(state):
        call_count["step2"] += 1
        return {"s2": True}
    def step3_crash(state):
        call_count["step3"] += 1
        raise RuntimeError("boom")
    
    add_node("step1", step1); add_node("step2", step2); add_node("step3", step3_crash)
    add_edge("step1", "step2"); add_edge("step2", "step3")
    set_entry("step1")
    
    cp = FileCheckpointer("test_state.json")
    
    # First run — crashes at step3
    try:
        run(checkpointer=cp)
    except RuntimeError:
        pass
    
    assert call_count == {"step1": 1, "step2": 1, "step3": 1}
    
    # Fix step3, resume
    def step3_fixed(state):
        call_count["step3"] += 1
        return {"s3": True}
    nodes["step3"] = step3_fixed
    
    result = run(checkpointer=cp)
    
    # step1 and step2 should NOT run again — count still 1
    assert call_count == {"step1": 1, "step2": 1, "step3": 2}, f"Got: {call_count}"
    assert result == {"s1": True, "s2": True, "s3": True}
    
    os.remove("test_state.json")
    print("✓ test_checkpoint_and_resume passed")


if __name__ == "__main__":
    test_linear_execution()
    test_reducer_appends()
    test_conditional_edge()
    test_max_iterations()
    test_streaming()
    test_checkpoint_and_resume()
    print("\n🎉 All tests passed")