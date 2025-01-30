from abc import abstractmethod

from src.models import ValidatedResult


class BaseValidator:
    def __init__(self, data):
        self.data = data

    @abstractmethod
    def validate(self) -> ValidatedResult:
        raise NotImplementedError