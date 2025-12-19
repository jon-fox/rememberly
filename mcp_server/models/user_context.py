"""User context for request handling."""

from typing import Optional, Dict, Any
from pydantic import BaseModel


class UserContext(BaseModel):
    """User context attached to requests.
    
    Authentication is based on email from the OAuth token, which is:
    - Always present in valid OAuth token claims
    - Unique per user
    - Verified by the OAuth authorization server
    
    The user_data from DynamoDB is optional and used for additional context,
    but is not required for authentication.
    """

    user_id: Optional[str] = None
    email: Optional[str] = None
    user_data: Optional[Dict[str, Any]] = None
    user_validated: bool = False

    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated and validated.
        
        Returns True if the user has a validated OAuth token with an email.
        Email is the primary validation key since it's unique and always
        present in the OAuth token claims.
        """
        return self.user_validated and self.email is not None
