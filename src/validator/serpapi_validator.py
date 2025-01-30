from openai import APIStatusError, AuthenticationError, OpenAI, RateLimitError
import rich

from src.models import ValidatedResult, ApiKeyStatus
from src.validator.base import BaseValidator


class SerpApiValidator(BaseValidator):
    def validate(self, key: str) -> ValidatedResult:
        return ValidatedResult(
            key=key,
            valid=ApiKeyStatus.VALID.value,
            remaining=1000,
        )
