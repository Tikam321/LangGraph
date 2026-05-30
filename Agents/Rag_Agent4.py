import os
from typing import Annotated, List, Sequence, TypedDict
from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph.message import add_messages;
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

# our embeddings
# embeddings = GoogleGenerativeAIEmbeddings(
#   model="embedding-001",
# )

# embeddings = GoogleGenerativeAIEmbeddings(
#   model="gemini-embedding-2-preview",
# )

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
pdf_path = "April_2026_Stock_Market_Analysis.pdf"

if not os.path.exists(pdf_path):
  raise FileExistsError(f"PDF file not found: {pdf_path}")

def load_pdf(path: str) -> list[Document]:
    reader = PdfReader(path)
    documents = []
    for i, page in enumerate(reader.pages):
       text = page.extract_text()
       if text.strip():
          documents.append(Document(page_content=text, metadata={'source':path, "page":i}))
    return documents

    # return [
    #     Document(page_content=page.extract_text(), metadata={"source": path, "page": i})
    #     for i, page in enumerate(reader.pages) if page.extract_text().strip()
    # ]

documents = load_pdf(pdf_path)

# print(f"pdf loader content {documents}")

# chunking process 
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = text_splitter.split_documents(documents)
chunks = [c for c in chunks if c.page_content.strip()]
print(chunks)

# embeddings(place where embeddings file will be stored)
persist_deirectory = "/Users/tikamsuvasiya/Documents/AI/Langchain/LangGraph/Agents"
collection_name = "stock_market"

# if collection does not exist then we will craete diractory
if not os.path.exists(persist_deirectory):
   os.mkdir(persist_deirectory)

try:
   vector_store = Chroma.from_documents(
      documents=chunks,
      embedding=embeddings,
      persist_directory=persist_deirectory,
      collection_name=collection_name
   )
   print(f"created vector chroma store")
except Exception as e:
   print(f"Error setting up chromadb")
   raise



retriver = vector_store.as_retriever(
   search_type="similarity",
   search_kwargs={"k":5} # k is the amount of chunks to return 
)

@tool
def retriver_tool(query: str) -> str:
   """
   This tool searches and return the information from the stock market performance.
   """

   docs = retriver.invoke(query)

   if not docs:
      return "I found no relevent information related to he query the user asked"
   
   results = []
   for i, doc in enumerate(docs):
      results.append(f"Document {i+1}:\n{doc.page_content}")
   return "\n\n".join(results)

tools = [retriver_tool]

# Initialize Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
).bind_tools(tools)


tools_dict = {our_tool.name: our_tool for our_tool in tools}

class AgentState(TypedDict):
   messages: Annotated[Sequence[BaseMessage], add_messages]

def should_continue(state:AgentState):
   """ Check if the last message contains tool calls"""
   result = state["messages"][-1]
   if hasattr(result, 'tool_calls') and len(result.tool_calls) > 0:
      return "continue"
   else:
      return "end"
   
system_prompt = """
You are an intelligent AI assistant specializing in stock market performance analysis.
You have access to a retriever tool that can fetch stock market performance data.
Your role is to answer user questions about stock market performance using the retriever tool.
Guidelines:
- Always use the retriever tool to fetch relevant data before answering.
- Present stock data clearly — include percentage changes, trends, and timeframes.
- If the retriever returns insufficient data, acknowledge the limitation.
- Do not make up stock data or numbers — only use what the retriever provides.
- Keep responses concise and focused on the user's question.
"""

def model_call(state: AgentState) -> AgentState:
  """ Function to call the LLm with the current state """
  # if not state["messages"]:
  #   user_input = "I'm ready to help you update a document. What would you like to create?\n"
  #   user_message = HumanMessage(content=user_input)
  # else:
  #   user_input = input("\nWhat would you like to do with the document? ")
  #   print(f"\n USER: {user_input}")
  #   user_message = HumanMessage(content=user_input)
  # messages = list(state["messages"])
  messages = [SystemMessage(content=system_prompt)] + list(state["messages"])
  messages = llm.invoke(messages)
  return {"messages": [messages]}



def take_action(state:AgentState):
   """ Execute the tool call from LLM's response """
   tool_calls = state["messages"][-1].tool_calls
   results = []
   result = ""
   for t in tool_calls:
      print(f"calling tool :{t['name']} with query :{t['args'].get('query', 'no query provided')}")

      if not t['name'] in tools_dict: # check if valid tool pis present ot not 
         print(f"\nTool: {t['name']} does not exist")
         result = "incorrect tool name , plese retry and select tool for list ofavilable tools"

      else:
         result = tools_dict[t['name']].invoke(t['args'].get('query', ''))
         print(f"result length {len(str(result))}")

      results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))

      print("Tools Execution Compelte. Back to the model")
   return {"messages": results}
   
   


graph = StateGraph(AgentState)
graph.add_node("model_node", model_call)
graph.add_node("retriver_agent", take_action)
graph.add_edge(START, "model_node")
graph.add_conditional_edges(
  "model_node",
  should_continue,
  {
    "end": END,
    "continue": "retriver_agent"
  }
)
graph.add_edge("retriver_agent", "model_node")

app = graph.compile()


def runnint_agent():
   print("\n RAG AGENT")
   while True:
      user_input = input("\nWhat is the question: ")
      if user_input.lower() in ['exit', 'quit']:
         break
      messages = [HumanMessage(content=user_input)] 
      result = app.invoke({'messages': messages})
      print("\n====ANSWER=====")
      print(result['messages'][-1].content)

if __name__ == "__main__":
  runnint_agent()

   
  
   







