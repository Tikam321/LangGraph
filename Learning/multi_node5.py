import math
from typing import List, TypedDict;
from langgraph.graph import StateGraph;

class AgentState(TypedDict):
  name: str
  age: str
  final: str

def first_node(state: AgentState) -> AgentState:
  """ This is first node of the sequence"""
  state["final"] = f"Hi {state["name"]}"
  return state

def second_node(state: AgentState) -> AgentState:
  """ This is second node of the sequence"""
  state["final"] = state["final"] + f" you are {state['age']} years old"
  return state


graph = StateGraph(AgentState);
graph.add_node("first_node", first_node);
graph.add_node("second_node", second_node)
graph.set_entry_point("first_node");
graph.add_edge("first_node", "second_node")
graph.set_finish_point("second_node");

app = graph.compile();

print(app.invoke({"name": "tikam", "age": "15"})["final"]);




