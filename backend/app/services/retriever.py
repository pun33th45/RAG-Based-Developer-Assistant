from pathlib import Path

from langchain_community.vectorstores import FAISS

from app.config import get_settings
from app.services.embedding import get_embeddings


def get_vector_store_path() -> Path:
    return get_settings().vector_store_path


def has_vector_store() -> bool:
    path = get_vector_store_path()
    return (path / "index.faiss").exists() and (path / "index.pkl").exists()


def create_or_update_vector_store(chunks):
    embeddings = get_embeddings()
    path = get_vector_store_path()

    if has_vector_store():
        store = FAISS.load_local(str(path), embeddings, allow_dangerous_deserialization=True)
        store.add_documents(chunks)
    else:
        store = FAISS.from_documents(chunks, embeddings)

    store.save_local(str(path))
    return store


def load_vector_store():
    if not has_vector_store():
        raise RuntimeError("No indexed documents found. Upload files before querying.")

    return FAISS.load_local(
        str(get_vector_store_path()),
        get_embeddings(),
        allow_dangerous_deserialization=True,
    )


def get_relevant_documents(question: str, k: int | None = None):
    settings = get_settings()
    store = load_vector_store()
    return store.similarity_search(question, k=k or settings.retrieval_k)
