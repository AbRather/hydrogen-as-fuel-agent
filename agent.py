import os
from dotenv import load_dotenv

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent 
from langchain_experimental.tools import PythonREPLTool

# New imports for the Vector Database
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# Initialize environment
load_dotenv()

# ==========================================
# TOOL 1: The Autonomous Data Analyst
# ==========================================
python_repl = PythonREPLTool()
python_repl.name = "python_data_analyst"
python_repl.description = (
    "A Python shell. Use this to execute pandas code to analyze data. "
    "The dataset is located at 'data/renewable_hydrogen_dataset_2535.csv'. "
    "If you want to see the output of a value, you MUST use the print() function."
)

# ==========================================
# TOOL 2: The Literature Researcher (RAG)
# ==========================================
# Connect to the Chroma database you just built!
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-small")
)

@tool
def search_hydrogen_specs(query: str) -> str:
    """
    Queries the internal engineering knowledge base (PDFs) for technical specifications, 
    costs, safety manuals, or literature regarding hydrogen and composite materials.
    """
    # Search the database for the top 3 most relevant paragraphs
    docs = vectorstore.similarity_search(query, k=3)
    
    if not docs:
        return "No relevant information found in the knowledge base."
    
    # Format the results so the LLM knows exactly which PDF it came from
    context = "\n\n".join([f"Source: {doc.metadata.get('source', 'Unknown')}\nExcerpt: {doc.page_content}" for doc in docs])
    return f"Found the following technical excerpts:\n{context}"

# ==========================================
# THE ORCHESTRATOR
# ==========================================
def build_agent_executor():
    """Constructs the LLM reasoning engine and binds engineering tools."""
    tools = [python_repl, search_hydrogen_specs]
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    system_instruction = (
        "You are a Lead Energy Data Engineer at EnBW specializing in hydrogen infrastructure. "
        "Use your tools to research literature and analyze CSV datasets. "
        "Always cite the exact PDF source or data calculation you used to reach your conclusion."
    )
    
    return create_agent(model=llm, tools=tools, system_prompt=system_instruction)

if __name__ == "__main__":
    agent_app = build_agent_executor()
    
    # 🚀 The Ultimate Multi-Tool Engineering Query
    query = (
        "I need a comprehensive report for our hydrogen infrastructure team. "
        "First, search the literature to tell me what materials are typically used for the liner "
        "and structural layers of a Type IV hydrogen storage tank. "
        "Second, use your python data analyst tool to analyze the renewable hydrogen dataset and "
        "tell me the maximum 'Hydrogen_Production_kg/day' recorded in the dataset."
    )
    
    print(f"User Query: {query}\n")
    print("-" * 40)
    
    try:
        response = agent_app.invoke({"messages": [("user", query)]})
        
        print("\n" + "=" * 40)
        print("FINAL REPORT:")
        print(response["messages"][-1].content)
        
    except Exception as e:
        print(f"Agent execution failed: {e}")