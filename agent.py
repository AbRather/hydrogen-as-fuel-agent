import os
import pandas as pd
from dotenv import load_dotenv

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent 
from langchain_experimental.tools import PythonREPLTool
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

# ==========================================
# 1. DIGITAL TWIN SIMULATOR
# ==========================================
@tool
def digital_twin_stress_test(pressure_mpa: float, temp_k: float) -> str:
    """
    Simulates structural integrity for Type IV Hydrogen Tanks using a 
    physics-informed Digital Twin. Essential for predictive maintenance.
    """
    # 2026 Aerospace Standards: Safety Factor of 2.25 for CFRP
    # Simplified Thin-Wall Pressure Vessel Stress: σ = (P * r) / t
    radius = 0.5  # meters
    thickness = 0.025  # meters (25mm Carbon Fiber)
    
    hoop_stress = (pressure_mpa * radius) / thickness
    
    # NASA/ESA 2026 Microcrack Resistance Threshold
    limit_mpa = 650.0 
    safety_margin = limit_mpa / hoop_stress if hoop_stress > 0 else 10.0
    
    status = "NOMINAL" if safety_margin >= 1.5 else "WARNING: MICROCRACK RISK"
    if safety_margin < 1.0: status = "CRITICAL: STRUCTURAL FAILURE"

    return (f"--- DIGITAL TWIN SIMULATION REPORT ---\n"
            f"Input: {pressure_mpa}MPa @ {temp_k}K\n"
            f"Calculated Hoop Stress: {hoop_stress:.2f} MPa\n"
            f"Current Safety Factor: {safety_margin:.2f}\n"
            f"Structural Status: {status}")

# ==========================================
# 2. EXPLAINABLE AI (XAI) SEARCH
# ==========================================
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-small")
)

@tool
def search_technical_specs(query: str) -> str:
    """
    Queries the Engineering Knowledge Base. Returns excerpts with 
    Full Metadata for regulatory compliance and auditability.
    """
    docs = vectorstore.similarity_search(query, k=2)
    
    # Returning structured metadata is key for 2026 XAI standards
    excerpts = []
    for doc in docs:
        meta = doc.metadata
        excerpts.append(
            f"SOURCE: {meta.get('source', 'Unknown')}\n"
            f"LOCATION: Page {meta.get('page', 'N/A')}\n"
            f"CONTENT: {doc.page_content}\n"
        )
    return "\n---\n".join(excerpts)

# ==========================================
# 3. ANOMALY DETECTION DATA TOOL
# ==========================================
python_repl = PythonREPLTool()
python_repl.description = (
    "A Python shell for data analysis. "
    "MANDATORY: You MUST use print() for ANY output you want to see (e.g., print(df.columns) or print(max_val)). "
    "MANDATORY: You must always 'import pandas as pd' and 'df = pd.read_csv(\"data/renewable_hydrogen_dataset_2535.csv\")' in your script. "
    "If production drops >20% or pressure exceeds 70MPa, flag it as an ANOMALY."
)

def build_agent_executor():
    tools = [python_repl, search_technical_specs, digital_twin_stress_test]
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    # Persona: EnBW System-Critical Infrastructure Lead
    system_instruction = (
        "You are the Lead Operational AI for EnBW's Hydrogen Backbone. "
        "1. Safety First: Use the digital_twin_stress_test for any pressure-related query. "
        "2. Transparency: Always cite sources with Page Numbers and filenames. "
        "3. Proactivity: If data analysis reveals a violation of specs, issue a CRITICAL ALARM."
    )
    
    return create_agent(model=llm, tools=tools, system_prompt=system_instruction)

if __name__ == "__main__":
    agent_app = build_agent_executor()
    
    query = (
        "We are evaluating a 75MPa operational load on a Type IV tank. "
        "1. Use the Digital Twin to check the safety margin. "
        "2. Search the specs to see if this pressure is allowed by ISO standards. "
        "3. Find the maximum hydrogen production in the dataset and flag if it's an anomaly."
    )
    
    response = agent_app.invoke({"messages": [("user", query)]})
    print("\n" + "="*50 + "\nOPERATIONAL COMMAND CENTER REPORT\n" + "="*50)
    print(response["messages"][-1].content)