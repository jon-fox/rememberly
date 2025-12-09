"""DateTime resource for providing current date and time information."""

from datetime import datetime, timezone
from typing import ClassVar, Optional, Type
from pydantic import BaseModel
from interfaces.resource import Resource, ResourceResponse, BaseResourceInput
from .models import DateTimeInput, DateTimeOutput


class DateTimeResource(Resource):
    """Resource that provides current date and time information."""

    name: ClassVar[str] = "current_datetime"
    description: ClassVar[str] = (
        "Provides the current date and time in various formats. "
        "Useful for timestamping operations, scheduling, and time-aware processing."
    )
    uri: ClassVar[str] = "datetime://current"
    mime_type: ClassVar[Optional[str]] = "application/json"
    input_model: ClassVar[Type[BaseResourceInput]] = DateTimeInput
    output_model: ClassVar[Type[BaseModel]] = DateTimeOutput

    async def read(self, input_data: BaseResourceInput) -> ResourceResponse:
        """Return current date and time information."""
        now = datetime.now(timezone.utc)

        output = DateTimeOutput(
            current_datetime=now.isoformat(),
            current_date=now.strftime("%Y-%m-%d"),
            current_time=now.strftime("%H:%M:%S"),
            timezone="UTC",
            unix_timestamp=int(now.timestamp()),
            day_of_week=now.strftime("%A"),
            year=now.year,
            month=now.month,
            day=now.day,
            hour=now.hour,
            minute=now.minute,
            second=now.second,
        )

        return ResourceResponse.from_model(output)
