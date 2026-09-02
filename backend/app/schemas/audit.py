from datetime import datetime

from pydantic import BaseModel

from .user import UserSummaryResponse


class AuditResponse(BaseModel):
    created_at: datetime
    created_by: UserSummaryResponse | None = None
    updated_at: datetime | None = None
    updated_by: UserSummaryResponse | None = None
