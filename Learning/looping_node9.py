
import math
import random
from typing import List, TypedDict;
from langgraph.graph import END, START, StateGraph;

class AgentState(TypedDict):
  name: str
  number: List[int]
  counter: int


def greting_node(state: AgentState) -> AgentState:
  """ this is greeting generator function"""
  state["name"] = f"Hi {state['name']}"
  state["counter"] = 0;
  return state


def random_node(state: AgentState) -> AgentState:
  """ generate random number generator from 1 to 10"""
  state["number"].append(random.randint(0,10))
  state["counter"] = state["counter"] + 1
  return state


def should_continue(state: AgentState) -> AgentState:
  """This function will return whether the loop continue ir not """
  if (state["counter"] < 5):
    print (f"entering LOOP {state["counter"]}")
    return "loop" # continue loop
  return "exit" # exit the loop



graph = StateGraph(AgentState);
graph.add_node("greeting_node", greting_node);
graph.add_node("random_node", random_node)
graph.add_edge(START, "greeting_node")
graph.add_edge("greeting_node", "random_node")

# conditional loop 
graph.add_conditional_edges(
  "random_node", # source node
  should_continue, # routing function
  {
    # Edge: node
    "loop": "random_node", # self loop back to same node
    "exit": END # exit loop
  }
)

graph.add_edge("random_node",END)
# data flow digram
# "greeting -> random -> random -> random -> random -> random -> random -> END"
app = graph.compile();
initial_state= {"name": "tikam", "number":[], "counter": -1}
print(app.invoke(initial_state));




