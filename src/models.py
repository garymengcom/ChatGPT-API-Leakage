from enum import Enum

from pydantic import BaseModel


class ValidatedResult(BaseModel):
    key: str
    valid: bool
    remaining: int = 0


class ApiKeyStatus(Enum):
    ADDED = "ADDED"
    VALID = "VALID"
    INVALID = "INVALID"
