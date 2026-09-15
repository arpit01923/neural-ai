from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from schemas.research import ResearchQuery, ResearchResponse
from services.research_history_service import delete_history_item, list_history, save_history_item
from services.research_service import generate_research_report
from services.report_generator import build_docx_bytes, build_markdown_report, build_pdf_bytes

router = APIRouter(prefix="/research", tags=["research"])


@router.post("", response_model=ResearchResponse)
async def create_research(query: ResearchQuery):
    if not query.query.strip():
        raise HTTPException(status_code=400, detail="Research question cannot be empty")

    try:        
        print(f"Saving research history for question: {query.query}")
        result = generate_research_report(query.query)
        print(f"Research report generated for question: {query.query}")
        save_history_item(query.query, result, result.get("sources", []))
    except Exception as exc:
        print(f"Error occurred while generating research report for question: {query.query}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return result


@router.get("/history")
async def get_research_history():
    return list_history()


@router.delete("/history/{item_id}")
async def delete_research_history(item_id: str):
    deleted = delete_history_item(item_id)
    return {"deleted": deleted}


@router.post("/export/markdown")
async def export_markdown(query: ResearchQuery):
    try:
        report = generate_research_report(query.query)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    markdown = build_markdown_report(report)
    return Response(
        content=markdown,
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=research-report.md"},
    )


@router.post("/export/pdf")
async def export_pdf(query: ResearchQuery):
    try:
        report = generate_research_report(query.query)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    pdf_bytes = build_pdf_bytes(report)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=research-report.pdf"},
    )


@router.post("/export/docx")
async def export_docx(query: ResearchQuery):
    try:
        report = generate_research_report(query.query)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    docx_bytes = build_docx_bytes(report)
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=research-report.docx"},
    )
