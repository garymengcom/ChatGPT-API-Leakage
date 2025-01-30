from openai import APIStatusError, AuthenticationError, OpenAI, RateLimitError
import rich

from src.models import ValidatedResult
from src.validator.base import BaseValidator


class SerpApiValidator(BaseValidator):
    def validate(self) -> ValidatedResult:
        return ValidatedResult(
            key="serpapi-key",
            valid=True,
            remaining=1000,
        )
