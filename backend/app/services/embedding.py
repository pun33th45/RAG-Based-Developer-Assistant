from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.embeddings import Embeddings

from app.config import get_settings


class GeminiEmbeddings(Embeddings):
    def __init__(self, model: str, api_key: str):
        self.client = GoogleGenerativeAIEmbeddings(
            model=model,
            google_api_key=api_key,
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # Some Gemini embedding backends return a single vector for batched input.
        # FAISS needs a strict one-document-to-one-vector mapping, so keep it explicit.
        return [self.client.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self.client.embed_query(text)


def get_embeddings() -> GeminiEmbeddings:
    settings = get_settings()
    api_key = settings.google_genai_api_key
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY or GEMINI_API_KEY is not configured.")

    return GeminiEmbeddings(model=settings.gemini_embedding_model, api_key=api_key)
