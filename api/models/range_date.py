from http import HTTPStatus
from typing import Optional
from fastapi import HTTPException
from pydantic import BaseModel, Field, model_validator, field_validator
from datetime import datetime, timedelta, timezone


class RangeDate(BaseModel):
    from_date: Optional[datetime] = Field(default=None, description="Start date (YYYY-MM-DD)")
    to_date: Optional[datetime] = Field(default=None, description="End date (YYYY-MM-DD)")

    @field_validator("from_date", "to_date", mode="before")
    def parse_date(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v)
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD")
        return v

    @model_validator(mode="after")
    def set_defaults_and_validate(self):

        if not self.from_date and not self.to_date:
            # only from_date is set to yesterday if both are missing
            today = datetime.now(timezone.utc)
            yesterday = today - timedelta(days=1)
            date = yesterday.replace(hour=23, minute=55, second=0, microsecond=0)
            self.from_date = date

        elif (self.from_date and not self.to_date) or (not self.from_date and self.to_date):
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail="Both 'from_date' and 'to_date' must be provided together"
            )

        if self.from_date and self.to_date and self.to_date < self.from_date:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail="'from_date' must be before or equal to 'to_date'"
            )

        return self
