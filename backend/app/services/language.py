from sqlalchemy.orm import Session

from ..models.language import Language
from ..repository.language import retrieve_all
from ..schemas.language import LanguageResponse


def retrieve_languages(db: Session) -> list[LanguageResponse]:
    languages: list[Language] = retrieve_all(db)
    return [LanguageResponse.model_validate(language) for language in languages]
