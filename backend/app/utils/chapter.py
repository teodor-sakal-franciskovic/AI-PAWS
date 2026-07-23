import re
from typing import List

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
