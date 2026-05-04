import logging

from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from app.services.rag_pipeline import answer_question
from app.utils.errors import safe_error_message


router = APIRouter(prefix="/query", tags=["query"])
logger = logging.getLogger("devinsight.query")


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=2)
    k: int | None = Field(default=None, ge=1, le=10)


@router.post("")
async def query(request: QueryRequest):
    try:
        logger.info("Received query: length=%s top_k=%s", len(request.question), request.k)
        return answer_question(request.question, request.k)
    except RuntimeError as exc:
        logger.warning("Query rejected: error=%s", safe_error_message(exc))
        raise HTTPException(status_code=400, detail=safe_error_message(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected query failure")
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {safe_error_message(exc)}") from exc
