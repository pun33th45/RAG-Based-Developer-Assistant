import zipfile
from io import BytesIO
from pathlib import Path

from fastapi import UploadFile
from langchain_core.documents import Document

from app.config import get_settings


ALLOWED_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".txt", ".md", ".json", ".yaml", ".yml", ".css", ".html"}
IGNORED_PARTS = {"node_modules", ".git", "__pycache__", "dist", "build", ".venv", "venv", ".idea", ".vscode"}


def is_allowed_file(path: Path) -> bool:
    return path.suffix.lower() in ALLOWED_EXTENSIONS


def is_ignored(path: Path) -> bool:
    return any(part in IGNORED_PARTS for part in path.parts)


def decode_text(data: bytes) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1", errors="ignore")


def build_document(source: str, suffix: str, text: str) -> Document | None:
    if not text.strip():
        return None

    return Document(page_content=text, metadata={"source": source, "file_type": suffix})


def validate_upload_size(data: bytes) -> None:
    settings = get_settings()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise ValueError(f"Upload exceeds {settings.max_upload_size_mb}MB limit.")


async def load_documents_from_upload(file: UploadFile) -> list[Document]:
    filename = file.filename or "upload"
    suffix = Path(filename).suffix.lower()
    data = await file.read()

    validate_upload_size(data)

    if suffix == ".zip":
        return load_documents_from_zip_bytes(data)

    path = Path(filename)
    if not is_allowed_file(path):
        raise ValueError("Unsupported file type.")

    document = build_document(path.name, suffix, decode_text(data))
    return [document] if document else []


def load_documents_from_zip_bytes(data: bytes) -> list[Document]:
    documents: list[Document] = []

    with zipfile.ZipFile(BytesIO(data)) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue

            member_path = Path(member.filename)
            validate_zip_member(member_path)
            if is_ignored(member_path) or not is_allowed_file(member_path):
                continue

            with archive.open(member) as handle:
                text = decode_text(handle.read())

            document = build_document(member.filename, member_path.suffix.lower(), text)
            if document:
                documents.append(document)

    return documents


def validate_zip_member(member_path: Path) -> None:
    # Reject path traversal before reading zip content into memory.
    if member_path.is_absolute() or ".." in member_path.parts:
        raise ValueError("Unsafe zip path detected.")


def load_documents(path: Path) -> list[Document]:
    root = path
    files = [root] if root.is_file() else [item for item in root.rglob("*") if item.is_file()]
    documents: list[Document] = []

    for file_path in files:
        if is_ignored(file_path) or not is_allowed_file(file_path):
            continue
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = file_path.read_text(encoding="latin-1")
        except OSError:
            continue

        if text.strip():
            document = build_document(
                str(file_path.relative_to(root.parent if root.is_file() else root)),
                file_path.suffix.lower(),
                text,
            )
            if document:
                documents.append(document)

    return documents
