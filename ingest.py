import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# Load your OpenAI API key
load_dotenv()

def build_vector_database():
    """Reads PDFs from the data folder, chunks them, and saves to ChromaDB."""
    
    print("📂 1. Scanning 'data' folder for PDFs...")
    # This automatically finds paper1.pdf, paper2.pdf, and paper3.pdf
    loader = PyPDFDirectoryLoader("data")
    documents = loader.load()
    
    if not documents:
        print("❌ No PDFs found. Make sure they are in the 'data' folder!")
        return

    print(f"📄 2. Loaded {len(documents)} total pages. Chopping into chunks...")
    
    # We split the text into 1000-character chunks with a 200-character overlap
    # The overlap ensures we don't accidentally cut a sentence in half!
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    
    print(f"✂️ 3. Split the papers into {len(chunks)} searchable chunks.")
    print("🧠 4. Generating OpenAI embeddings and building ChromaDB...")
    
    # This connects to OpenAI, turns the text to math, and saves it locally
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
        persist_directory="./chroma_db"  # This is where the database will be saved
    )
    
    print("✅ 5. SUCCESS! Vector database built at './chroma_db'")

if __name__ == "__main__":
    build_vector_database()