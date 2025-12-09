"""Models for DateTime resource."""

from pydantic import BaseModel, Field
from interfaces.resource import BaseResourceInput


class DateTimeInput(BaseResourceInput):
    """Input model for datetime resource - no parameters needed."""
    pass


class DateTimeOutput(BaseModel):
    """Output model for datetime resource."""

    current_datetime: str = Field(
        ..., description="Current date and time in ISO 8601 format"
    )
    current_date: str = Field(..., description="Current date (YYYY-MM-DD)")
    current_time: str = Field(..., description="Current time (HH:MM:SS)")
    timezone: str = Field(..., description="Timezone (UTC)")
    unix_timestamp: int = Field(..., description="Unix timestamp in seconds")
    day_of_week: str = Field(..., description="Day of the week")
    year: int = Field(..., description="Current year")
    month: int = Field(..., description="Current month (1-12)")
    day: int = Field(..., description="Current day of month (1-31)")
    hour: int = Field(..., description="Current hour (0-23)")
    minute: int = Field(..., description="Current minute (0-59)")
    second: int = Field(..., description="Current second (0-59)")
