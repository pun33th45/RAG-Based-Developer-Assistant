from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import get_settings


CODE_SEPARATORS = [
    "\nclass ",
    "\ndef ",
    "\nfunction ",
    "\nconst ",
    "\nexport ",
    "\n\n",
    "\n",
    " ",
    "",
]


def chunk_documents(documents):
    settings = get_settings()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=CODE_SEPARATORS,
    )
    return splitter.split_documents(documents)
