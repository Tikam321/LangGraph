import os
from typing import Annotated, List, Sequence, TypedDict;
from langgraph.graph import END, START, StateGraph;
from langgraph.graph.message import add_messages;
from langchain_core.tools import tool
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.prebuilt import ToolNode

load_dotenv()

class AgentState(TypedDict):
  messages: Annotated[Sequence[BaseMessage], add_messages]


@tool
def add(a: int, b:int):
  """ This is the addition function which return the addition"""
  return a+b

@tool
def substract(a: int, b:int):
  """ This is the substraction function which return the substraction"""
  return a-b

tools = [add, substract]

# Initialize Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
).bind_tools(tools)

def model_call(state:AgentState) -> AgentState:
  system_message = SystemMessage(content="You are my AI assistent, please answer my to the best of your knowledge")
  response = llm.invoke([system_message] + state["messages"])
  print(state["messages"])
  return {"messages": [response]}


def should_continue(state: AgentState) -> AgentState:
  """ This is basically router function which routes the request from model_call to tool node"""
  message = state["messages"]
  lastMessage = message[-1]
  if not lastMessage.tool_calls:
    return "end"
  return "continue"


graph = StateGraph(AgentState)
graph.add_node("model_node", model_call)
tool_node = ToolNode(tools=tools)
graph.add_node("tool_node", tool_node)
graph.add_edge(START, "model_node")
graph.add_conditional_edges(
  "model_node",
  should_continue,
  {
    "end": END,
    "continue": "tool_node"
  }
)

graph.add_edge("tool_node", "model_node")

app = graph.compile()

# app.invoke({"messages": "cna you add 1 +2"})

def print_stream(stream):
  for s in stream:
    message = s["messages"][-1]
    if isinstance(message, tuple):
      print(message)
    else:
      message.pretty_print()

input = { "messages": [HumanMessage(content="Add 100 and 12 and then substract 100")]}
print_stream(app.stream(input, stream_mode="values"))