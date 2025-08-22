from pydantic import BaseModel


class SubmissionModeResponse(BaseModel):
    id: int
    name: str
    description: str
