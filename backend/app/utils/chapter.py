import re
from typing import Dict, List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..repository.chapter import retrieve_all
from .logger import logger

_CYRILLIC_TO_LATIN_MAP = {
    "А": "A",
    "а": "a",
    "Б": "B",
    "б": "b",
    "В": "V",
    "в": "v",
    "Г": "G",
    "г": "g",
    "Д": "D",
    "д": "d",
    "Ђ": "Đ",
    "ђ": "đ",
    "Е": "E",
    "е": "e",
    "Ж": "Ž",
    "ж": "ž",
    "З": "Z",
    "з": "z",
    "И": "I",
    "и": "i",
    "Ј": "J",
    "ј": "j",
    "К": "K",
    "к": "k",
    "Л": "L",
    "л": "l",
    "Љ": "Lj",
    "љ": "lj",
    "М": "M",
    "м": "m",
    "Н": "N",
    "н": "n",
    "Њ": "Nj",
    "њ": "nj",
    "О": "O",
    "о": "o",
    "П": "P",
    "п": "p",
    "Р": "R",
    "р": "r",
    "С": "S",
    "с": "s",
    "Т": "T",
    "т": "t",
    "Ћ": "Ć",
    "ћ": "ć",
    "У": "U",
    "у": "u",
    "Ф": "F",
    "ф": "f",
    "Х": "H",
    "х": "h",
    "Ц": "C",
    "ц": "c",
    "Ч": "Č",
    "ч": "č",
    "Џ": "Dž",
    "џ": "dž",
    "Ш": "Š",
    "ш": "š",
}


def convert_to_latin(text: str) -> str:
    logger.info("Converting text to latin...")
    converted_text = []
    for char in text:
        converted_text.append(_CYRILLIC_TO_LATIN_MAP.get(char, char))
    logger.info("Successfully converted markdown text to latin.")
    return "".join(converted_text)


def normalise_title(text: str) -> str:
    logger.info(f"Normalising input for {text}...")
    text = text.replace("_", " ")
    no_internal_spaces = re.sub(r"\s+", "", text)
    logger.info(f"Successfully normalised input {text}")
    return convert_to_latin(no_internal_spaces).strip().upper()


def get_valid_chapter_titles(db: Session) -> List[str]:
    logger.info("Fetching chapter titles from database...")
    chapters = retrieve_all(db)
    valid_names = [chapter.name for chapter in chapters]
    valid_names.append("RJEŠENJE")  # TODO: Discuss ijekavica
    return [normalise_title(name) for name in valid_names]


def find_chapter_matches(text: str) -> List[re.Match]:
    pattern = re.compile(
        r"^(?P<num>[IVXLC]+)\.?\s+(?P<title>[A-ZĆČŽŠĐ\s]+)$", re.MULTILINE
    )
    matches = list(pattern.finditer(text))
    if not matches:
        logger.warning("No chapter headers found using the pattern.")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No chapter headers found in the document.",
        )
    return matches


def identify_valid_chapters(
    matches: List[re.Match], valid_titles: List[str]
) -> List[Dict]:
    chapters = []
    for match in matches:
        raw_title = match.group("title")
        normalised_title = normalise_title(raw_title)
        if normalised_title in valid_titles:
            chapters.append({"title": normalised_title, "start": match.start()})
    return chapters


def get_end_of_document(text: str) -> int:
    pattern = r"^(?P<lit>(?:L)?\s*I\s*T\s*E\s*R\s*A\s*T\s*U\s*R\s*A)$"
    match = re.search(pattern, text, re.MULTILINE)
    return match.start() if match else len(text)


def add_chapter_end_indices(chapters: List[Dict], end_of_text: int) -> None:
    for i, chapter in enumerate(chapters):
        chapter["end"] = (
            chapters[i + 1]["start"] if i + 1 < len(chapters) else end_of_text
        )


def extract_chapter_by_title(text: str, chapters: List[Dict], target_title: str) -> str:
    for chapter in chapters:
        if chapter["title"] == target_title:
            chapter_text = text[chapter["start"] : chapter["end"]].strip()

            # Remove the title line
            lines = chapter_text.splitlines()
            content_lines = lines[1:] if len(lines) > 1 else []

            cleaned = " ".join(content_lines).replace("\n", "").strip()
            return cleaned

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=f"Chapter '{target_title}' not found.",
    )
