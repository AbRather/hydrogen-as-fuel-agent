# 🚀 Autonomous Hydrogen Research Agent
**Domain:** Aerospace Engineering | Hydrogen Energy | Agentic AI

An autonomous "Reasoning Engine" built with **LangChain V1.0** that assists engineers in synthesizing technical literature and analyzing large-scale energy datasets.

## 🏗️ Architecture
The system utilizes a **Tool-Calling Agent** pattern to bridge the gap between unstructured text (PDFs) and structured data (CSVs).

* **Knowledge Base (RAG):** A ChromaDB vector store containing peer-reviewed research on Type IV composite hydrogen storage tanks.
* **Data Analyst (Python REPL):** A sandboxed Python environment allowing the Agent to write and execute `pandas` code dynamically to analyze 2,500+ rows of renewable hydrogen production data.
* **Self-Correction:** The Agent is capable of inspecting data schemas (column names) at runtime to prevent pipeline crashes.

## 🛠️ Tech Stack
* **Orchestration:** LangChain V1.0 / LangGraph
* **LLM:** GPT-4o
* **Vector DB:** ChromaDB (OpenAI Embeddings)
* **Data Science:** Pandas, NumPy
* **Language:** Python 3.13

## 📊 Sample Execution
The agent can answer complex, multi-stage queries such as:
> *"Research the liner materials for Type IV tanks in the literature, then calculate the average production capacity from the CSV for locations meeting those spec requirements."*