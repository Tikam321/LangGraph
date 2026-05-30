"""
1. Accept user's name, age and list of their skills
2. pass the state through three nodes that 
first node: personlizes the name field  with greeting 
second node: describer users age
third node: list the users skills in a formatted string
the final output in the result field should be combined message in this format
output: tikam welcome to the system! you are 31 years old you have skills in: python macine learnig and langgraph
"""

import math
from typing import List, TypedDict;
from langgraph.graph import StateGraph;

class AgentState(TypedDict):
  name: str
  age: str
  final: str
  skills: List[str]

def first_node(state: AgentState) -> AgentState:
  """ This is first node of the sequence"""
  state["final"] = f"Hi {state["name"]}"
  return state

def second_node(state: AgentState) -> AgentState:
  """ This is second node of the sequence"""
  state["final"] = state["final"] + f" you are {state['age']} years old"
  return state

def third_node(state: AgentState) -> AgentState:
  """ This is second node of the sequence"""
  state["final"] = state["final"] + f" you have skills in {state['skills']}"
  return state

graph = StateGraph(AgentState);
graph.add_node("first_node", first_node)
graph.add_node("second_node", second_node)
graph.add_node("third_node", third_node)

graph.set_entry_point("first_node");
graph.add_edge("first_node", "second_node")
graph.add_edge("second_node", "third_node")

graph.set_finish_point("third_node");

app = graph.compile();

print(app.invoke({"name": "tikam", "age": "15", "skills":"python and langgraph"})["final"]);




