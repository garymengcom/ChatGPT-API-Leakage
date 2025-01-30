from abc import abstractmethod

from src.models import ValidatedResult


class BaseValidator:
    @abstractmethod
    def validate(self, key: str) -> ValidatedResult:
        raise NotImplementedError