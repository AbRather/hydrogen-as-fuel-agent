import os
import shutil
import traceback
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import AIMessage, ToolMessage

from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from agent import build_agent_executor

os.makedirs("./data", exist_ok=True)
os.makedirs("./chroma_db", exist_ok=True)

app = FastAPI(title="GenAI Architecture PoC", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    prompt: str

class FeedbackRequest(BaseModel):
    query: str
    response: str
    is_positive: bool

# --- INGESTION PIPELINE ---
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        file_path = f"./data/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        if file.filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        else:
            raise HTTPException(status_code=400, detail="Please upload a PDF.")
            
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        splits = text_splitter.split_documents(docs)
        
        vectorstore = Chroma(
            persist_directory="./chroma_db", 
            embedding_function=OpenAIEmbeddings(model="text-embedding-3-small")
        )
        vectorstore.add_documents(splits)
        return {"status": "success", "message": f"Ingested {len(splits)} chunks."}
    except Exception as e:
        print("🚨 UPLOAD ERROR:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# --- AGENT ORCHESTRATION ---
@app.post("/analyze")
async def analyze_infrastructure(request: QueryRequest):
    try:
        agent_app = build_agent_executor()
        response = agent_app.invoke({"messages": [("user", request.prompt)]})
        
        reasoning_steps = []
        for msg in response["messages"]:
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    reasoning_steps.append({
                        "step": len(reasoning_steps) + 1,
                        "event": f"Triggered: {tool_call['name']}"
                    })

        content = {
            "status": "success",
            "final_report": response["messages"][-1].content,
            "explainability_log": reasoning_steps
        }
        return JSONResponse(content=content)
    except Exception as e:
        print("\n" + "!"*50)
        print("🚨 CRITICAL BACKEND ERROR 🚨")
        traceback.print_exc()
        print("!"*50 + "\n")
        raise HTTPException(status_code=500, detail=str(e))

# --- EVALUATION & TELEMETRY ---
@app.post("/feedback")
async def log_feedback(request: FeedbackRequest):
    log_entry = {
        "query": request.query,
        "is_positive": request.is_positive,
        "status": "Logged to Evaluation DB"
    }
    print(f"TELEMETRY LOGGED: {log_entry}")
    return {"status": "success", "message": "Feedback recorded for model evaluation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)