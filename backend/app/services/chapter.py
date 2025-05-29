import os
import tempfile

# https://pypi.org/project/pymupdf4llm/
import pymupdf4llm
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..utils.logger import logger


def extract_pdf_to_markdown(file_bytes: bytes, db: Session):
    logger.info("Storing the file at a temporary location...")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_path = temp_file.name
        temp_file.write(file_bytes)
        temp_file.flush()

    try:
        logger.info("Retrieving markdown text from pdf text for the file...")
        markdown_text = pymupdf4llm.to_markdown(temp_path)
    except Exception as e:
        logger.error(f"Error: 500; Parsing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    if not markdown_text:
        logger.error("Error: 500; No content was extracted from the document.")
        raise HTTPException(
            status_code=500, detail="No content was extracted from the document."
        )
    logger.info("Successfully converted pdf to markdown text")

    return markdown_text
