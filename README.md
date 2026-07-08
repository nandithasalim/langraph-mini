---
Built by [Nanditha](https://github.com/nandithasalim) while learning how agent frameworks work internally.
# minigraph

A minimal LangGraph-style agent framework, built from scratch in ~150 lines of pure Python. No dependencies.

I built this to understand how agent orchestration frameworks work internally. It supports everything the real LangGraph does at its core: state, reducers, conditional edges, cycles, streaming, and checkpointing with resume-from-node.

## Example

```python
from minigraph import add_node, add_edge, set_entry, run

def greet(state):
    return {"greeting": f"Hello, {state['name']}"}

def shout(state):
    return {"loud": state["greeting"].upper()}

add_node("greet", greet)
add_node("shout", shout)
add_edge("greet", "shout")
set_entry("greet")

print(run({"name": "Nanditha"}))
# → {'name': 'Nanditha', 'greeting': 'Hello, Nanditha', 'loud': 'HELLO, NANDITHA'}
```

## Features

- **Nodes and edges** — register functions as nodes, wire them in a directed graph
- **Shared state** — a dict passed to every node; each node returns partial updates
- **Reducers** — custom per-key merging (e.g. `append_reducer` for accumulating chat history) instead of default overwrite
- **Conditional edges** — routing that depends on state (`if age >= 18: allow_voting else deny_voting`)
- **Cycles with safety** — max-iteration guard prevents infinite loops from misconfigured routing
- **Streaming** — `stream()` yields state after each node for real-time UX and debugging
- **Checkpointing with resume** — save state + next node to disk; on crash, resume from where you left off without re-running completed nodes

## Running a real production pipeline on it

I rebuilt the 3-node LangGraph pipeline from my project MotivAI (retrieve context → generate reaction → store) on top of minigraph. Same node structure, same state model, identical behavior — see `motivai_rebuild.py`.

## Test

Run the built-in test suite (7 tests covering every feature):

python3 test.py

Run the MotivAI production pipeline rebuild on top of minigraph:

python3 motivai_rebuild.py

Seven tests cover every feature end-to-end, including a crash-and-resume test that proves completed nodes don't re-run on resume.

## Why I built this

I was using LangGraph in production for MotivAI and realized I couldn't confidently explain what happens when a node crashes mid-run, or how state reducers work under the hood, or what checkpointing actually persists. So I rebuilt the core myself. Turns out the whole execution engine fits in a few hundred lines — the rest of LangGraph is dedicated backends, async support, and integrations.

Understanding it end-to-end changed how I debug and design agent pipelines. Sharing in case it helps anyone else.