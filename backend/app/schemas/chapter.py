from pydantic import BaseModel


class ChapterResponse(BaseModel):
    id: int
    name: str
