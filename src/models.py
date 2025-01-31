from enum import Enum
from pydantic import BaseModel


class ApiKeyStatus(Enum):
    ADDED = "ADDED"
    VALID = "VALID"
    INVALID = "INVALID"


class ValidatedResult(BaseModel):
    key: str
    valid: ApiKeyStatus
    total: int
    remaining: int
