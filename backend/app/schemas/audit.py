from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .user import UserSummaryResponse


class AuditResponse(BaseModel):
    created_at: datetime
    created_by: Optional[UserSummaryResponse] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[UserSummaryResponse] = None
