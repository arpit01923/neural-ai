import os
from typing import List, Dict, Any

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama

from config import settings


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHROMA_PERSIST_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")


os.makedirs(CHROMA_PERSIST_DIRECTORY, exist_ok=True)
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def split_text_into_chunks(text: str, chunk_size: int = 800, chunk_overlap: int = 120) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    return splitter.split_text(text)


def extract_text_from_pdf(file_path: str) -> str:
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    return "\n\n".join(page.page_content for page in documents if getattr(page, "page_content", None))


def build_vector_store(text: str, document_id: str) -> Dict[str, Any]:
    chunks = split_text_into_chunks(text)
    if not chunks:
        raise ValueError("No text could be extracted from the provided PDF")

    vector_store = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PERSIST_DIRECTORY,
        collection_name=document_id,
        metadatas=[{"source": f"{document_id}.pdf", "document_id": document_id} for _ in chunks],
    )
    vector_store.persist()
    return {"document_id": document_id, "chunk_count": len(chunks)}


def query_document(query: str, document_id: str, chat_history: List[Dict[str, str]] | None = None) -> Dict[str, Any]:
    vector_store = Chroma(
        collection_name=document_id,
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIRECTORY,
    )

    docs = vector_store.similarity_search(query, k=4)
    context = "\n\n".join(doc.page_content for doc in docs)
    llm = Ollama(model=settings.OLLAMA_MODEL, base_url=settings.OLLAMA_URL)

    history_text = ""
    if chat_history:
        history_text = "\n".join(f"{entry.get('role')}: {entry.get('content', '')}" for entry in chat_history)

    prompt = (
        "Use the provided context to answer the user's question. "
        "If the answer is not present in the context, say that you do not know.\n\n"
        f"Conversation history:\n{history_text}\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}"
    )
    answer = llm.invoke(prompt)
    sources = [doc.metadata.get("source", "unknown") for doc in docs]
    return {"answer": answer, "sources": sources, "context": context}


def process_pdf(file_path: str, document_id: str) -> Dict[str, Any]:
    text = extract_text_from_pdf(file_path)
    return build_vector_store(text, document_id)
