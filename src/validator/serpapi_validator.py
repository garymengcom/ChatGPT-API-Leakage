import requests

from src.models import ValidatedResult, ApiKeyStatus
from src.validator.base import BaseValidator


class SerpApiValidator(BaseValidator):

    def validate(self, key: str) -> ValidatedResult:
        url = f"https://serpapi.com/account?api_key={key}"
        response = requests.get(url)

        if response.status_code != 200:
            return ValidatedResult(
                key=key,
                valid=ApiKeyStatus.INVALID.value,
                total=0,
                remaining=0,
            )

        result = response.json()
        return ValidatedResult(
            key=key,
            valid=ApiKeyStatus.VALID.value,
            total=result.get("searches_per_month", 0),
            remaining=result.get("plan_searches_left", 0),
        )


if __name__ == '__main__':
    r = SerpApiValidator().validate("3708e00dbee0ad944a3a1d9af9b7df47f13d3d7bfa2ea4d82d8e9dbf255d4ac7")
    print(r)