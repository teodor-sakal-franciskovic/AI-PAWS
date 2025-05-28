from datetime import datetime

from pydantic import BaseModel


class GroupCreate(BaseModel):
    name: str
    valid_from: datetime
    valid_until: datetime

    def __str__(self):
        return (
            f"GroupCreate(name='{self.name}', "
            f"valid_from='{self.valid_from.strftime('%Y-%m-%d %H:%M:%S')}', "
            f"valid_until='{self.valid_until.strftime('%Y-%m-%d %H:%M:%S')}')"
        )