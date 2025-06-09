import os
import re
import tempfile

# https://pypi.org/project/pymupdf4llm/
import pymupdf4llm
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..repository.chapter import retrieve_all

from ..utils.logger import logger
from ..utils.chapter import normalise_title, to_latin


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


def extract_chapter_text(markdown_text: str, chapter_name: str, db: Session):
    logger.info("Converting text to latin...")
    latin_markdown_text = to_latin(markdown_text)
    logger.info("Successfully converted markdown text to latin.")

    logger.info(f"Normalising input for {chapter_name}...")
    normalised_input = normalise_title(chapter_name)
    logger.info(f"Successfully normalised input: '{normalised_input}'")

    chapters = retrieve_all(db)

    valid_chapters_raw = [chapter.name for chapter in chapters]
    # TODO - Discuss ijekavica
    valid_chapters_raw.append("RJEŠENJE")
    logger.info(f"Valid chapters raw {valid_chapters_raw}")

    normalised_valid_chapters = [normalise_title(name) for name in valid_chapters_raw]
    logger.info(f"Normalised valid chapters: {normalised_valid_chapters}")

    chapter_header_pattern = re.compile(
        r"^(?P<num>[IVXLC]+)\.?\s+(?P<title>[A-ZĆČŽŠĐ\s]+)$", re.MULTILINE
    )
    logger.info(latin_markdown_text)
    matches = list(chapter_header_pattern.finditer(latin_markdown_text))
    if not matches:
        logger.warning("No chapter headers found using the pattern.")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No chapter headers found in the document.",
        )

    chapters = []
    logger.info("Iterating through regex matches to identify chapters:")
    for match in matches:
        raw_title = match.group("title")
        start_index = match.start()
        logger.info(f"Raw match found: '{raw_title}' at index {start_index}")

        title = normalise_title(raw_title)
        logger.info(f"Normalised matched title: '{title}'")

        if title in normalised_valid_chapters:
            logger.info(f"'{title}' is a valid chapter. Adding to chapters list.")
            chapters.append(
                {
                    "title": title,
                    "start": start_index,
                }
            )
        else:
            logger.info(f"  '{title}' is NOT in the list of valid chapters. Skipping.")

    logger.info(f"Identified chapters before calculating end points: {chapters}")

    references_match = re.search(
        r"^(?P<lit>L\s*I\s*T\s*E\s*R\s*A\s*T\s*U\s*R\s*A)$",
        latin_markdown_text,
        re.MULTILINE,
    )
    end_of_text = (
        references_match.start() if references_match else len(latin_markdown_text)
    )
    logger.info(
        f"End of document determined by LITERATURA or full length: {end_of_text}"
    )

    if not chapters:
        logger.info(
            f"No valid chapters identified in the document matching: {normalised_valid_chapters}"
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No valid chapters found in the document.",
        )

    for idx, chapter in enumerate(chapters):
        next_start = (
            chapters[idx + 1]["start"] if idx + 1 < len(chapters) else end_of_text
        )
        chapter["end"] = next_start
        logger.info(
            f"Chapter '{chapter['title']}' calculated start: {chapter['start']}, end: {chapter['end']}"
        )

    for chapter in chapters:
        if chapter["title"] == normalised_input:
            logger.info(f"Returning text for {chapter_name} chapter...")
            extracted_text = latin_markdown_text[
                chapter["start"] : chapter["end"]
            ].strip()
            logger.info(f"Extracted text length: {len(extracted_text)}")
            return extracted_text

    logger.info(
        f"Chapter {chapter_name} was not found among the identified valid chapters."
    )
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=f"Chapter '{chapter_name}' not found.",
    )
