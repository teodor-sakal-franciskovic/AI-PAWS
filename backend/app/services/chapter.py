import os
import re
import tempfile

# https://pypi.org/project/pymupdf4llm/
import pymupdf4llm
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..utils.chapter import (
    add_chapter_end_indices,
    convert_to_latin,
    extract_chapter_by_title,
    find_chapter_matches,
    get_end_of_document,
    get_valid_chapter_titles,
    identify_valid_chapters,
    normalise_title,
)
from ..utils.logger import logger


def extract_pdf_to_markdown(file_bytes: bytes):
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


def extract_chapter_text(markdown_text: str, chapter_name: str, db: Session) -> str:
    latin_text = convert_to_latin(markdown_text)
    normalised_target = normalise_title(chapter_name)
    valid_titles = get_valid_chapter_titles(db)
    matches = find_chapter_matches(latin_text)
    chapters = identify_valid_chapters(matches, valid_titles)

    if not chapters:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No valid chapters found in the document.",
        )

    end_of_text = get_end_of_document(latin_text)
    add_chapter_end_indices(chapters, end_of_text)

    extracted = extract_chapter_by_title(latin_text, chapters, normalised_target)
    logger.info(f"Extracted chapter '{chapter_name}' with length {len(extracted)}")
    return extracted
