import requests

from src.core.models import ValidatedResult, ApiKeyStatus


def serpapi_validate(key: str) -> ValidatedResult:
    url = f"https://serpapi.com/account?api_key={key}"
    response = requests.get(url)

    if response.status_code != 200:
        return ValidatedResult(
            key=key,
            status=ApiKeyStatus.INVALID,
            total=0,
            remaining=0,
        )

    result = response.json()
    return ValidatedResult(
        key=key,
        status=ApiKeyStatus.VALID,
        total=result.get("searches_per_month", 0),
        remaining=result.get("plan_searches_left", 0),
    )
