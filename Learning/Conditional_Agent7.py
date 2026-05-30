
import math
from typing import List, TypedDict;
from langgraph.graph import END, START, StateGraph;

class AgentState(TypedDict):
  number1: int
  operation: str
  number2: int
  finalNumber: int


def adder(state: AgentState) -> AgentState:
  """ This node adds the 2 number"""
  state["finalNumber"] = state["number1"] + state["number2"]
  return state

def substractor(state: AgentState) -> AgentState:
  """ This node substract the 2 numbers"""
  state["finalNumber"] = state["number1"] - state["number2"]
  return state


def decide_next_node(state:AgentState) -> AgentState:
  "This node will select the next node of graph"
  if state["operation"] == "+":
    return "addition_operation"
  elif state["operation"] == "-":
    return "substraction_operation"
  


graph = StateGraph(AgentState);
graph.add_node("adder_node", adder);
graph.add_node("subtractor_node", substractor)
graph.add_node("router", lambda state:state) # passthough function
graph.add_edge(START, "router")

graph.add_conditional_edges(
  "router",
  decide_next_node,
  {
    # Edge: node
    "addition_operation": "adder_node",
    "substraction_operation": "subtractor_node"
  }
)

graph.add_edge("adder_node", END)
graph.add_edge("router", END)

app = graph.compile();
initial_state1= {"number1": 5, "number2": 2, "operation": "+"}
print(app.invoke(initial_state1)["finalNumber"]);




