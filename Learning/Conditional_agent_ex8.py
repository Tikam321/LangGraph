
"""
task: make teh graph on the right you will need to make use of 2 conditional edges
input: initial_state = Agentstate(number1 = 10,operatoin="*",
number2=6,number3=7,number4=2,opeartion="+",finalNumber=0,finalNumber2=0)
"""

import math
from typing import List, TypedDict;
from langgraph.graph import END, START, StateGraph;

class AgentState(TypedDict):
  number1: int
  operation1: str
  number2: int
  number3: int
  number4: int
  operation2: int
  finalNumber1: int
  finalNumber2: int

def adder1(state: AgentState) -> AgentState:
  """ This node adds the 2 number"""
  state["finalNumber1"] = state["number1"] + state["number2"]
  return state

def substractor1(state: AgentState) -> AgentState:
  """ This node substract the 2 numbers"""
  state["finalNumber1"] = state["number1"] - state["number2"]
  return state

def adder2(state: AgentState) -> AgentState:
  """ This node adds the 2 number"""
  state["finalNumber2"] = state["number3"] + state["number4"]
  return state

def substractor2(state: AgentState) -> AgentState:
  """ This node substract the 2 numbers"""
  state["finalNumber2"] = state["number3"] - state["number4"]
  return state


def decide_next_node1(state:AgentState) -> AgentState:
  "This node will select the next node(router1) of graph"
  if state["operation1"] == "+":
    return "addition_operation1"
  elif state["operation1"] == "-":
    return "substraction_operation1"
  
def decide_next_node2(state:AgentState) -> AgentState:
  "This node will select the next node(router2) of graph"
  if state["operation2"] == "+":
    return "addition_operation2"
  elif state["operation2"] == "-":
    return "substraction_operation2"

graph = StateGraph(AgentState);
graph.add_node("adder_node1", adder1);
graph.add_node("subtractor_node1", substractor1)
graph.add_node("adder_node2", adder2);
graph.add_node("subtractor_node2", substractor2)
graph.add_node("router1", lambda state:state) # passthough function
graph.add_node("router2", lambda state:state) # passthough function
graph.add_edge(START, "router1")



graph.add_conditional_edges(
  "router1",
  decide_next_node1,
  {
    # Edge: node
    "addition_operation1": "adder_node1",
    "substraction_operation1": "subtractor_node1"
  }
)
graph.add_edge("adder_node1", "router2")
graph.add_edge("subtractor_node1", "router2")

graph.add_conditional_edges(
  "router2",
  decide_next_node2,
  {
    # Edge: node
    "addition_operation2": "adder_node2",
    "substraction_operation2": "subtractor_node2"
  }
)

graph.add_edge("adder_node2", END)
graph.add_edge("subtractor_node2", END)

app = graph.compile();
initial_state1= {"number1": 5, "number2": 2,"number3": 8, "number4": 4, "operation1": "+", "operation2": "-"}
print(app.invoke(initial_state1));




