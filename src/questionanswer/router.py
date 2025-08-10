from fastapi import APIRouter, status, UploadFile, File
from fastapi.responses import JSONResponse
from src.questionanswer.chunking import DocumentChunker
from src.questionanswer.qdrant_db import QdrantConfig
from src.questionanswer.schemas import UploadChunkSchema
from fastapi import HTTPException
from src.questionanswer.workflow import create_workflow

workflow = create_workflow()
config = QdrantConfig()
chunker = DocumentChunker()

router = APIRouter(prefix="", tags=["QuestionandAnsewr"])


@router.post("chunkpdf/", status_code=status.HTTP_201_CREATED)
async def process_pdf(file: UploadFile = File(...)):
    """Process pdf file"""
    try:
        # Save uploaded file temporarily
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        # Run chunking and summarization
        md_header_splits = chunker.pdf_to_markdown(temp_path)
        markdown_chunks = [split.page_content for split in md_header_splits]
        summaries = chunker.create_summary(markdown_chunks)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "message": "PDF processed successfully.",
                "markdown_chunks": markdown_chunks,
                "summaries": summaries,
            },
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Error processing PDF")


@router.post("uploadchunk/", status_code=status.HTTP_201_CREATED)
async def upload_chunk(request: UploadChunkSchema):
    """Upload docs to qdrant"""
    try:
        config.upsert_documents(request.summaries, request.metadata)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "message": "Chunks uploaded to Qdrant successfully.",
            },
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Error uploading chunks")


@router.post("/chat")
async def chat_with_user(query: str):
    try:
        initial_query = {"question": query}
        response = workflow.invoke(initial_query)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "Chat response generated successfully.",
                "response": response["generation"],
            },
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Error generating chat response")
