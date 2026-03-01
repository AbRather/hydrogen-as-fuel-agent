import uvicorn
import json
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from langchain_core.messages import AIMessage, ToolMessage

# Import the brain we built in the other file
from agent import build_agent_executor

app = FastAPI(
    title="Hydrogen Engineering Agent API",
    description="Operational AI for Hydrogen Infrastructure with XAI Audit Trails.",
    version="1.0.0"
)

# 1. Define the input structure
class QueryRequest(BaseModel):
    prompt: str

@app.post("/analyze")
async def analyze_infrastructure(request: QueryRequest):
    """
    Primary endpoint for engineering queries. 
    Returns the final report plus a detailed reasoning audit log.
    """
    # Initialize the agent
    agent_app = build_agent_executor()
    
    # Run the agent through its thought process
    # The 'messages' list will capture every thought and tool execution
    response = agent_app.invoke({"messages": [("user", request.prompt)]})
    
    # 2. Build the Explainability Log (The Audit Trail)
    # We loop through the internal message history to show the "Why"
    reasoning_steps = []
    for msg in response["messages"]:
        # Capture when the AI decides to use a specific tool
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tool_call in msg.tool_calls:
                reasoning_steps.append({
                    "step": len(reasoning_steps) + 1,
                    "event": "AI_DECISION",
                    "action": f"Executing Tool: {tool_call['name']}",
                    "logic_input": tool_call['args']
                })
        
        # Capture what the tool actually returned to the AI
        elif isinstance(msg, ToolMessage):
            reasoning_steps.append({
                "step": len(reasoning_steps) + 1,
                "event": "TOOL_OBSERVATION",
                "output_data": msg.content[:300] + "..." if len(msg.content) > 300 else msg.content
            })

    # 3. Construct the structured response
    # We use a JSONResponse to ensure it is sent back as clean, ordered JSON
    content = {
        "status": "success",
        "query_received": request.prompt,
        "final_report": response["messages"][-1].content,
        "explainability_log": reasoning_steps
    }
    
    return JSONResponse(
        content=content, 
        media_type="application/json"
    )

if __name__ == "__main__":
    # Run the server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)