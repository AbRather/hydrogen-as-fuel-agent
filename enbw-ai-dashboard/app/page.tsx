"use client";

import { useState, ChangeEvent, FormEvent, useRef, useEffect } from "react";

type ExplainabilityStep = {
  step: number;
  event: string;
};

type Message = {
  role: "user" | "agent";
  content: string;
  logs?: ExplainabilityStep[];
  feedbackSent?: boolean;
};

export default function Dashboard() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");

  const messagesEndRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) setFile(e.target.files[0]);
  };

  const uploadFile = async () => {
    if (!file) return;
    setIsUploading(true);
    setUploadStatus("Uploading to RAG Pipeline...");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      setUploadStatus(response.ok ? `✅ ${data.message}` : `❌ Error: ${data.detail}`);
      if (response.ok) setFile(null);
    } catch {
      setUploadStatus("❌ Server connection error.");
    }
    setIsUploading(false);
  };

  const sendMessage = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    const userQuery = input;
    setMessages((prev) => [...prev, { role: "user", content: userQuery }]);
    setInput("");
    setIsThinking(true);

    try {
      const response = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: userQuery }),
      });
      const data = await response.json();
      if (response.ok) {
        setMessages((prev) => [...prev, { role: "agent", content: data.final_report, logs: data.explainability_log }]);
      } else {
        // Expose the EXACT error message from FastAPI here
        setMessages((prev) => [...prev, { role: "agent", content: `❌ Backend Error: ${data.detail || "Unknown error"}` }]);
      }
    } catch {
      setMessages((prev) => [...prev, { role: "agent", content: "❌ Connection Error. Is FastAPI running?" }]);
    }
    setIsThinking(false);
  };

  const sendFeedback = async (msgIndex: number, isPositive: boolean) => {
    const userQuery = messages[msgIndex - 1]?.content || "Unknown query";
    const agentResponse = messages[msgIndex].content;

    try {
      await fetch("http://localhost:8000/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userQuery, response: agentResponse, is_positive: isPositive }),
      });
      
      setMessages((prev) => 
        prev.map((msg, idx) => idx === msgIndex ? { ...msg, feedbackSent: true } : msg)
      );
    } catch (error) {
      console.error("Failed to log feedback");
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans flex flex-col md:flex-row">
      <div className="w-full md:w-1/3 bg-white border-r p-6 flex flex-col">
        <h1 className="text-2xl font-bold text-blue-700 mb-2">GenAI Architecture PoC</h1>
        <p className="text-sm text-slate-500 mb-8">Agent Framework & Evaluation Testing</p>

        <div className="bg-slate-50 border border-dashed rounded-lg p-6 flex flex-col items-center mb-4">
          <h3 className="font-semibold mb-1">RAG Pipeline Ingestion</h3>
          <input type="file" accept=".pdf" onChange={handleFileChange} className="text-sm file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 mb-4 w-full"/>
          <button onClick={uploadFile} disabled={!file || isUploading} className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded disabled:opacity-50">
            {isUploading ? "Processing..." : "Upload to AI Search"}
          </button>
        </div>
        {uploadStatus && <div className="text-sm p-3 rounded bg-blue-50 text-blue-800">{uploadStatus}</div>}
      </div>

      <div className="w-full md:w-2/3 flex flex-col h-screen">
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
             <div className="flex flex-col items-center justify-center h-full text-slate-400">
               <p>System Ready. Test the Agent Framework.</p>
             </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}>
                <div className={`max-w-[80%] p-4 rounded-lg shadow-sm ${msg.role === "user" ? "bg-blue-600 text-white" : "bg-white border border-slate-200"}`}>
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>
                
                {msg.logs && msg.logs.length > 0 && (
                  <div className="mt-2 text-xs text-slate-500 font-mono">
                    {msg.logs.map((log, lIdx) => <span key={lIdx}>⚙️ {log.event} </span>)}
                  </div>
                )}

                {msg.role === "agent" && !msg.content.includes("❌") && !msg.feedbackSent && (
                  <div className="mt-2 flex gap-2">
                    <button onClick={() => sendFeedback(idx, true)} className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded hover:bg-green-200">👍 Accurate</button>
                    <button onClick={() => sendFeedback(idx, false)} className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded hover:bg-red-200">👎 Hallucination</button>
                  </div>
                )}
                {msg.feedbackSent && <span className="text-xs text-slate-400 mt-2">Feedback logged to telemetry.</span>}
              </div>
            ))
          )}
          {isThinking && <div className="animate-pulse text-slate-500">Agent is orchestrating tools...</div>}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 bg-white border-t border-slate-200">
          <form onSubmit={sendMessage} className="flex gap-2">
            <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Run a test scenario..." className="flex-1 p-3 border rounded-lg focus:outline-none" disabled={isThinking}/>
            <button type="submit" disabled={isThinking || !input.trim()} className="bg-blue-600 text-white px-6 py-3 rounded-lg disabled:opacity-50">Send</button>
          </form>
        </div>
      </div>
    </div>
  );
}