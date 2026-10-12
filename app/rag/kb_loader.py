import os
from typing import List

from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document

KB_DIR = os.path.join(os.path.dirname(__file__), "docs")


def build_vector_store(kb_dir: str = KB_DIR, persist_path: str = None):
    """Load plain text files from kb_dir into an in-memory FAISS vectorstore.
    Returns (vectorstore, embedder)
    """
    texts: List[Document] = []
    if not os.path.exists(kb_dir):
        os.makedirs(kb_dir, exist_ok=True)
        # Create a sample runbook
        with open(os.path.join(kb_dir, "sample_runbook.md"), "w", encoding="utf-8") as f:
            f.write("""
# Sample Runbook

If P99 latency > 800ms and success_rate < 0.98, try increasing sender thread pool and reduce retries.
""")

    for fname in os.listdir(kb_dir):
        path = os.path.join(kb_dir, fname)
        if os.path.isfile(path) and path.endswith(".md"):
            with open(path, "r", encoding="utf-8") as f:
                texts.append(Document(page_content=f.read(), metadata={"source": path}))

    embedder = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    if texts:
        vectorstore = FAISS.from_documents(texts, embedder)
    else:
        vectorstore = FAISS.from_documents([Document(page_content="empty", metadata={})], embedder)

    return vectorstore, embedder


def get_retriever(k: int = 4):
    vs, emb = build_vector_store()
    return vs.as_retriever(search_kwargs={"k": k})
