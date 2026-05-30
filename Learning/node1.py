from typing import TypedDict;
from langgraph.graph import StateGraph;

class AgentState(TypedDict):
  message: str

def greeting_node(state: AgentState) -> AgentState:
  """ Simple node that addes a greting message to state"""
  state['message'] = "Hello," + state['message'] + " , how are you doing today123?";
  return state;

def greeting_node_2(state: AgentState) -> AgentState:
  """ Simple node that addes a greting message to state"""
  state['message'] = state["message"] + "I am fine Today, thank you for asking!" ;
  return state;


graph = StateGraph(AgentState)
graph.add_node("greeter", greeting_node)
graph.add_node("greeter_2", greeting_node_2)
graph.add_edge("greeter", "greeter_2")
graph.set_entry_point("greeter")
graph.set_finish_point("greeter_2")

app = graph.compile()

print(app.invoke({"message": "Tikam"})["message"])





