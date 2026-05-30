
import math
import random
from typing import List, TypedDict;
from langgraph.graph import END, START, StateGraph;

class AgentState(TypedDict):
  name: str
  guesses: List[int]
  attempts: int
  lower_bound: int
  upper_bound: int
  target_number: int

def setup_node(state: AgentState) -> AgentState:
  """ this is greeting generator function"""
  print("game setup is done.")
  state["name"] = "tikam"
  state["attempts"] = 0
  state["lower_bound"] = 1
  state["upper_bound"] = 50
  state["target_number"] = random.randint(1, 50)
  state["guesses"] = []
  return state


def guess_node(state: AgentState) -> AgentState:
  """ this is guess function which generate random number [1,20]"""
  state["guesses"].append(random.randint(state["lower_bound"], state["upper_bound"]))
  state["attempts"] = state["attempts"] + 1;
  return state;


def hint_node(state: AgentState) -> AgentState:
  """ it will guess the node based on the number"""
  if state["guesses"][-1] < state["target_number"]:
    print(f"lower_bound is updated to {state['guesses'][-1]+1}")
    state["lower_bound"] = state["guesses"][-1]+1
  else:
    print(f"upper_bound is updated to {state['guesses'][-1]-1}")
    state["upper_bound"] = state["guesses"][-1]-1
  return state

def should_continue(state: AgentState) -> AgentState:
  "thi is rounter function it routes node based on the condition"
  if state["guesses"][-1] == state["target_number"]:
    print(f"{state['name']} guessed the number {state['target_number']} succesfully.")
    return "exit"
  elif state["attempts"] > 7:
    print(f"{state['name']} you have reached the maximum limit")
    return "exit"
  return "loop"

  



graph = StateGraph(AgentState);
graph.add_node("guess_node", guess_node)
graph.add_node("setup_node",setup_node)
graph.add_node("hint_node", hint_node)
graph.add_edge(START, "setup_node")
graph.add_edge("setup_node", "guess_node")
graph.add_edge("guess_node", "hint_node")


# conditional loop 
graph.add_conditional_edges(
  "hint_node", # source node
  should_continue, # routing function
  {
    # Edge: node
    "loop": "guess_node", # self loop back to same node
    "exit": END # exit loop
  }
)

graph.add_edge("hint_node",END)
# data flow digram
# "greeting -> random -> random -> random -> random -> random -> random -> END"
app = graph.compile();
initial_state= {"name": "tikam", "guesses": [], "attempts": 0, "lower_bound": 0, "upper_bound": 20}
print(app.invoke(initial_state));




