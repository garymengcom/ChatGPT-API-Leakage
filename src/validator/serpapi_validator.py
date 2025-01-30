from openai import APIStatusError, AuthenticationError, OpenAI, RateLimitError
import rich

from src.models import ValidatedResult
from src.validator.base import BaseValidator


class SerpApiValidator(BaseValidator):
    def validate(self, key: str) -> ValidatedResult:
        return ValidatedResult(
            key=key,
            valid=True,
            remaining=1000,
        )
