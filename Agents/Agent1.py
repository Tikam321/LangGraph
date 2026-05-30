import os
from typing import List, TypedDict;
from langgraph.graph import END, START, StateGraph;
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
load_dotenv()

# Initialize Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

class AgentState(TypedDict):
  messages: List[HumanMessage]

def process_node(state: AgentState) -> AgentState:
  """ Simple node that return the llm response """
  response = llm.invoke(state["messages"])
  print(f"AI: {response.content}")
  return state;


graph = StateGraph(AgentState)
graph.add_node("process_node", process_node)
graph.add_edge(START, "process_node")
graph.add_edge("process_node", END)

app = graph.compile()
user_input = input("Enter: ")

while user_input != "exit":
  app.invoke({"messages": [HumanMessage(user_input)]})
  user_input = input("Enter ")





