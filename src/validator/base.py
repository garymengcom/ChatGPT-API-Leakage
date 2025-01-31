from abc import abstractmethod

from src.core.models import ValidatedResult


class BaseValidator:
    @abstractmethod
    def validate(self, key: str) -> ValidatedResult:
        raise NotImplementedError