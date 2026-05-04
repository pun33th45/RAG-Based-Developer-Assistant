from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import get_settings
from app.services.retriever import get_relevant_documents


SYSTEM_PROMPT = "You are a senior developer. Explain code clearly and identify bugs if present."

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            """
Use the retrieved context to answer the user's question.

Guidelines:
- Be precise and practical.
- Cite file paths from the context when relevant.
- If the answer is not present in the context, say what is missing.
- For bug-finding requests, include severity, location, why it matters, and a suggested fix.

Question:
{question}

Context:
{context}
""",
        ),
    ]
)


def format_context(documents) -> str:
    blocks = []
    for index, doc in enumerate(documents, start=1):
        source = doc.metadata.get("source", "unknown")
        blocks.append(f"[{index}] Source: {source}\n{doc.page_content}")
    return "\n\n---\n\n".join(blocks)


def answer_question(question: str, k: int | None = None) -> dict:
    settings = get_settings()
    documents = get_relevant_documents(question, k=k)
    context = format_context(documents)
    api_key = settings.google_genai_api_key

    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY or GEMINI_API_KEY is not configured.")

    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_chat_model,
        google_api_key=api_key,
        temperature=0.2,
        max_retries=2,
    )

    chain = PROMPT | llm | StrOutputParser()
    answer = chain.invoke({"question": question, "context": context})

    return {
        "answer": answer,
        "sources": [
            {
                "source": doc.metadata.get("source", "unknown"),
                "file_type": doc.metadata.get("file_type", ""),
                "content": doc.page_content,
            }
            for doc in documents
        ],
    }
