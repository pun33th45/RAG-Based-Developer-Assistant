import shutil
import zipfile
from io import BytesIO
from pathlib import Path
from uuid import uuid4

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


async def load_documents_from_upload(file: UploadFile) -> list[Document]:
    settings = get_settings()
    filename = file.filename or "upload"
    suffix = Path(filename).suffix.lower()
    data = await file.read()

    if len(data) > settings.max_upload_size_mb * 1024 * 1024:
        raise ValueError(f"Upload exceeds {settings.max_upload_size_mb}MB limit.")

    if suffix == ".zip":
        return load_documents_from_zip_bytes(data)

    path = Path(filename)
    if not is_allowed_file(path):
        raise ValueError("Unsupported file type.")

    text = decode_text(data)
    if not text.strip():
        return []

    return [
        Document(
            page_content=text,
            metadata={"source": path.name, "file_type": suffix},
        )
    ]


def load_documents_from_zip_bytes(data: bytes) -> list[Document]:
    documents: list[Document] = []

    with zipfile.ZipFile(BytesIO(data)) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue

            member_path = Path(member.filename)
            if member_path.is_absolute() or ".." in member_path.parts:
                raise ValueError("Unsafe zip path detected.")
            if is_ignored(member_path) or not is_allowed_file(member_path):
                continue

            with archive.open(member) as handle:
                text = decode_text(handle.read())

            if text.strip():
                documents.append(
                    Document(
                        page_content=text,
                        metadata={
                            "source": member.filename,
                            "file_type": member_path.suffix.lower(),
                        },
                    )
                )

    return documents


async def save_upload(file: UploadFile) -> Path:
    settings = get_settings()
    suffix = Path(file.filename or "upload").suffix
    destination = settings.upload_dir / f"{uuid4().hex}{suffix}"

    size = 0
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    with destination.open("wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > max_bytes:
                destination.unlink(missing_ok=True)
                raise ValueError(f"Upload exceeds {settings.max_upload_size_mb}MB limit.")
            buffer.write(chunk)

    return destination


def extract_if_zip(path: Path) -> Path:
    if path.suffix.lower() != ".zip":
        return path

    extract_dir = path.with_suffix("")
    extract_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(path) as archive:
        for member in archive.infolist():
            target = (extract_dir / member.filename).resolve()
            if not str(target).startswith(str(extract_dir.resolve())):
                raise ValueError("Unsafe zip path detected.")
        archive.extractall(extract_dir)

    return extract_dir


def cleanup_path(path: Path) -> None:
    try:
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        else:
            path.unlink(missing_ok=True)
    except OSError:
        # Windows, OneDrive, or antivirus scanners can briefly lock fresh uploads.
        # Cleanup is best-effort and should not make a successful index look failed.
        pass


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
            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": str(file_path.relative_to(root.parent if root.is_file() else root)),
                        "file_type": file_path.suffix.lower(),
                    },
                )
            )

    return documents
