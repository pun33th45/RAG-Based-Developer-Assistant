from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.retriever import create_or_update_vector_store
from app.utils.chunking import chunk_documents
from app.utils.errors import safe_error_message
from app.utils.file_loader import load_documents_from_upload


router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("")
async def upload_file(file: UploadFile = File(...)):
    try:
        documents = await load_documents_from_upload(file)

        if not documents:
            raise HTTPException(status_code=400, detail="No supported readable files found.")

        chunks = chunk_documents(documents)
        create_or_update_vector_store(chunks)

        return {
            "message": "Upload indexed successfully.",
            "filename": file.filename,
            "documents": len(documents),
            "chunks": len(chunks),
        }
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to process upload: {safe_error_message(exc)}") from exc
    finally:
        await file.close()
