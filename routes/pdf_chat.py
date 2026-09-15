import os
import uuid
from typing import List, Dict, Any

from fastapi import APIRouter, File, UploadFile, HTTPException, Form

from services.pdf_chat_service import process_pdf, query_document

router = APIRouter(prefix="/pdf-chat", tags=["pdf-chat"])


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a valid PDF file")

    temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    os.makedirs(temp_dir, exist_ok=True)
    document_id = str(uuid.uuid4())
    temp_path = os.path.join(temp_dir, f"{document_id}.pdf")

    contents = await file.read()
    with open(temp_path, "wb") as handle:
        handle.write(contents)

    try:
        result = process_pdf(temp_path, document_id)
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"document_id": document_id, "message": "PDF processed successfully", **result}


@router.post("/query")
async def query_pdf(
    document_id: str = Form(...),
    question: str = Form(...),
    chat_history: List[Dict[str, str]] | None = None,
):
    if not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = query_document(question, document_id, chat_history)
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return result
