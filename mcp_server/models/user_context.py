"""User context for request handling."""

from typing import Optional, Dict, Any
from pydantic import BaseModel


class UserContext(BaseModel):
    """User context attached to requests.

    Authentication is based on email from the access token.
    The user_data from DynamoDB is optional and used for additional context.
    """

    user_id: Optional[str] = None
    email: Optional[str] = None
    user_data: Optional[Dict[str, Any]] = None
    user_validated: bool = False

    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated and validated."""
        return self.user_validated and self.email is not None
