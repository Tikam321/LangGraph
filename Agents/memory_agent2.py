import os
from typing import List, TypedDict, Union;
from langgraph.graph import END, START, StateGraph;
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage
load_dotenv()

# Initialize Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

class AgentState(TypedDict):
  messages: List[Union[HumanMessage | AIMessage]]

def process_node(state: AgentState) -> AgentState:
  """ this node solve the request you input """
  response = llm.invoke(state["messages"])
  state["messages"].append(AIMessage(content=response.content))
  print(f"AI: {response.content}")
  # print(f"CURRENT STATE {state['messages']}")
  return state;

graph = StateGraph(AgentState)
graph.add_node("process_node", process_node)
graph.add_edge(START, "process_node")
graph.add_edge("process_node", END)
app = graph.compile()

conversation_history = []
user_input = input("Enter: ")

while user_input != "exit":
  conversation_history.append(HumanMessage(content=user_input))
  print(f"human -> {HumanMessage(content=user_input)}")
  result = app.invoke({"messages": conversation_history})
  conversation_history = result["messages"]
  user_input = input("Enter ")


with open("logging.txt", "w") as file:
  file.write("Your Conversational history")
  for message in conversation_history:
    if isinstance(message, HumanMessage):
      file.write(f"You: {message.content}\n")
    elif isinstance(message,AIMessage):
      file.write(f"AI:{message.content}")
  
  file.write("End of Conversation")

print("Conversation saved to logging.txt")






