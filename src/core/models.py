from enum import Enum
from re import Pattern

from pydantic import BaseModel


class ApiKeyStatus(Enum):
    ADDED = "ADDED"
    VALID = "VALID"
    INVALID = "INVALID"


class ValidatedResult(BaseModel):
    key: str
    status: ApiKeyStatus
    total: int
    remaining: int


class UrlRegex(BaseModel):
    url: str
    regex: Pattern