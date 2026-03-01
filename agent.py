import os
from dotenv import load_dotenv

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langgraph.prebuilt import create_react_agent

load_dotenv()

# ==========================================
# TOOL 1: RAG PIPELINE
# ==========================================
@tool
def search_knowledge_base(query: str) -> str:
    """
    ALWAYS use this tool to search for documents, guidelines, manuals, PDFs, or CSVs.
    Returns technical excerpts to ground the AI's response and prevent hallucinations.
    """
    try:
        vectorstore = Chroma(
            persist_directory="./chroma_db",
            embedding_function=OpenAIEmbeddings(model="text-embedding-3-small")
        )
        docs = vectorstore.similarity_search(query, k=3)
        if not docs:
            return "No documents found. Ask the user to upload the reference file."
        
        excerpts = [f"[Page {d.metadata.get('page', 'N/A')}] {d.page_content}" for d in docs]
        return "\n\n".join(excerpts)
    except Exception as e:
        return f"Database error: {str(e)}"

# ==========================================
# TOOL 2: CAPABILITY PROTOTYPE
# ==========================================
@tool
def calculate_safety_margin(pressure_bar: float) -> str:
    """
    Calculates the safety margin for a standard pipeline.
    Input must be a numeric pressure value in bar.
    """
    max_safe_pressure = 1000.0
    margin = max_safe_pressure - pressure_bar
    if margin < 0:
        return f"CRITICAL WARNING: Pressure {pressure_bar} exceeds limits by {abs(margin)} bar."
    return f"Status Nominal. Remaining pressure capacity: {margin} bar."

# ==========================================
# ORCHESTRATOR 
# ==========================================
def build_agent_executor():
    tools = [search_knowledge_base, calculate_safety_margin]
    # Ensure your .env has OPENAI_API_KEY
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    system_instruction = (
        "You are an Enterprise AI Architecture. "
        "Your goal is to evaluate technical queries. "
        "If asked about documents, use search_knowledge_base. "
        "If asked about pressure or safety, use calculate_safety_margin. "
        "Always be transparent about which tool you used."
    )
    
    return create_react_agent(llm, tools, prompt=system_instruction)