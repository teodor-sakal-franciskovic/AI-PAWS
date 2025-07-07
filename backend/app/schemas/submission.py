from pydantic import BaseModel
from typing import Any
from datetime import datetime


class SubmissionResponse(BaseModel):
    id: int
    submitted_at: datetime
    text: str
    gd_file_id: str
    gd_file_link: str
    achieved_points: Any
    submission_mode: str
