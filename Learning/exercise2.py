
from typing import TypedDict;
from langgraph.graph import StateGraph;

"""
create a personalised compleiment agent using langGraph
input: {"name": "tikam"}
output: "Hello tikam, you are doing amazing job learning LangGraph!"
"""

class AgentState(TypedDict):
  name: str
  

def compliment_node(state: AgentState) -> AgentState:
  """ Simple node that addes a greting message to state"""
  state['name'] = "Hello " + state['name'] + ", you are doing amazing job learning LangGraph!";
  return state;

graph = StateGraph(AgentState)
graph.add_node("complimenter", compliment_node)
graph.set_entry_point("complimenter")
graph.set_finish_point("complimenter")

app = graph.compile()

print(app.invoke({"name": "Tikam"})["name"])

