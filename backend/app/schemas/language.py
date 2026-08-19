from pydantic import BaseModel


class LanguageResponse(BaseModel):
    id: int
    name: str
    short_name: str

    class Config:
        from_attributes = True
