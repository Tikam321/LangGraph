from typing import List, TypedDict;
from langgraph.graph import StateGraph;

class AgentState(TypedDict):
  values: List[int]
  name: str
  result: str

def processValues(state: AgentState) -> AgentState:
  """ This function handles multiples different inputs"""
  print(state)
  state["result"] = f"Hi there {state['name']}! Your sum is = {sum(state['values'])}"
  print(state)
  return state


graph = StateGraph(AgentState)
graph.add_node("processor", processValues)
graph.set_entry_point("processor")
graph.set_finish_point("processor")

app = graph.compile();
print(app.invoke({"values": [1,2,4,5,6],"name": "tikam"})["result"])
