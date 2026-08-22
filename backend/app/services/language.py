from sqlalchemy.orm import Session

from ..exceptions import ApiError
from ..models.language import Language
from ..repository.language import retrieve_all, retrieve_by_id, soft_delete
from ..schemas.language import LanguageResponse


def retrieve_languages(db: Session) -> list[LanguageResponse]:
    languages: list[Language] = retrieve_all(db)
    return [LanguageResponse.model_validate(language) for language in languages]


def delete_language(db: Session, language_id: int) -> None:
    language = retrieve_by_id(db, language_id)
    if not language:
        raise ApiError(404, "LANGUAGE_NOT_FOUND", "Language not found.")
    soft_delete(db, language)
