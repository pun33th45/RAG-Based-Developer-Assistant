from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from app.services.rag_pipeline import answer_question
from app.utils.errors import safe_error_message


router = APIRouter(prefix="/query", tags=["query"])


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=2)
    k: int | None = Field(default=None, ge=1, le=10)


@router.post("")
async def query(request: QueryRequest):
    try:
        return answer_question(request.question, request.k)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=safe_error_message(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {safe_error_message(exc)}") from exc
