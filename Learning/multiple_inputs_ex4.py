"""
create a graph where you pass in a single list of integer along with name and an
operation.if the operation is a "+", you add the elements and if it is a "*", you 
multiple the elements, all whithin the same node
input: {"name": "tikam", values:[1,2,4], "operation":"*"}
output: "hi jack sparrow your output is 24
"""
import math
from typing import List, TypedDict;
from langgraph.graph import StateGraph;


class AgentState(TypedDict):
  name: str
  values: List[int]
  operation: str
  result: str


def aggregator(state: AgentState) -> AgentState:
  """ this function handle the  processing the list based on the operation"""
  
  if (state['operation'] == "+"):
    print("+ operation");
    ans = sum(state['values']);
  else:
    print("multiplication operation");
    ans = math.prod(state["values"]);
  
  state['result'] = f"Hi {state['name']}, your ans is {ans}";
  return state;


graph = StateGraph(AgentState);
graph.add_node("processor", aggregator);
graph.set_entry_point("processor");
graph.set_finish_point("processor");

app = graph.compile();

print(app.invoke({"name": "tikam", "values": [1,2,3,4,5], "operation":"*"})["result"]);




