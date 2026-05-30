import os
from typing import Annotated, Sequence, TypedDict
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.prebuilt import ToolNode

load_dotenv()

document_content = ""

class AgentState(TypedDict):
  messages: Annotated[Sequence[BaseMessage], add_messages]

@tool
def update(content: str) -> str:
  """ Updates the document with provided content"""
  global document_content
  document_content = content
  return f"Document has been updated successfully the current content is ${document_content}"

@tool
def saved(filename: str) -> str:
  """ saved tool will be called when user want to save the final draft in .txt form an you can give the name according to the draft about and finish the process
       filename: Name for the text file
  """
  
  global document_content
  if not filename.endswith('.txt'):
    filename = f"{filename}.txt"

  try:
    with open(filename, 'w') as file:
      file.write(document_content)
    print(f"Document has been saved to {filename}")
    return f"Document has been saved successfully to {filename}."
  except Exception as e:
    return f"Error saving document: {str(e)}"
  
tools = [update, saved]

# Initialize Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
).bind_tools(tools)

def our_agent(state: AgentState) -> AgentState:
  system_message = SystemMessage(content=f"""
 You are my AI assistant, you are a document drafter. Help the user update and save the document.
 - if the user wants to update or modify content, use the 'update' tool with the complete updated content
 - if the user wants to save and finish, use the 'saved' tool
 - always show the current document state after modification.
 the current document content is: {document_content}
""")
  if not state["messages"]:
    user_input = "I'm ready to help you update a document. What would you like to create?"
    user_message = HumanMessage(content=user_input)
  else:
    user_input = input("\nWhat would you like to do with the document? ")
    print(f"\n USER: {user_input}")
    user_message = HumanMessage(content=user_input)
  
  all_messages = [system_message] + list(state["messages"]) + [user_message]
  response  = llm.invoke(all_messages)
  print(f"AI: {response.content}")
  if hasattr(response, "tool_calls") and response.tool_calls:
    print(f"USING TOOLS: {[tc['name'] for tc in response.tool_calls]}")
  return {"messages": list(state["messages"]) + [user_message, response]}

def should_continue(state: AgentState) -> str:
  messages = state["messages"]
  for message in reversed(messages):
    if isinstance(message, ToolMessage) and "saved" in message.content.lower():
      return "end"
  return "continue"

def print_message(messages):
  """Function made to print the messages in a more readable format"""
  if not messages:
    return
  
  for message in messages[-3:]:
    if isinstance(message, ToolMessage):
      print(f"TOOL RESULT: {message.content}")

graph = StateGraph(AgentState)
graph.add_node("model_node", our_agent)
tool_node = ToolNode(tools=tools)
graph.add_node("tool_node", tool_node)
graph.add_edge(START, "model_node")
graph.add_edge("model_node","tool_node")
graph.add_conditional_edges(
  "tool_node",
  should_continue,
  {
    "end": END,
    "continue": "model_node"
  }
)
app = graph.compile()
# app.invoke({"messages": "cna you add 1 +2"})
def run_document_agent():
  print("\n ==== DRAFTER ====== ")
  state = {"messages": []}
  for step in app.stream(state, stream_mode="values"):
    if "messages" in step:
      print_message(step["messages"])

  print("DRAFTER FINISHED")

if __name__ == "__main__":
  run_document_agent()

  