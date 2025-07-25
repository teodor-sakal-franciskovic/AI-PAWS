from ..services.chapter import (
    extract_pdf_to_markdown,
    extract_chapter_text,
    retrieve_chapters,
    retrieve_chapter_object_by_id,
)


def get_extract_pdf_to_markdown():
    return extract_pdf_to_markdown


def get_extract_chapter_text():
    return extract_chapter_text


def get_retrieve_chapters():
    return retrieve_chapters


def get_retrieve_chapter_object_by_id():
    return retrieve_chapter_object_by_id
