from typing import List

from src.db.engine import DbSession
from src.db.entity import ApiKey
from src.core.logging_utils import get_today, get_now
from src.core.models import ValidatedResult, ApiKeyStatus


class ApiKeyDao:
    @staticmethod
    def batch_add(website_name: str, api_keys: List[str]):
        with DbSession() as session:
            for api_key in api_keys:
                if not session.query(ApiKey.id).filter(ApiKey.website == website_name, ApiKey.api_key == api_key).scalar():
                    session.add(ApiKey(
                        website=website_name,
                        api_key=api_key,
                        status=ApiKeyStatus.ADDED.value,
                        remaining=0,
                        last_validated_at=get_now()))
            session.commit()

    @staticmethod
    def add_one(website_name: str, api_key: str, validated_result: ValidatedResult):
        with DbSession() as session:
            if not session.query(ApiKey.id).filter(ApiKey.website == website_name, ApiKey.api_key == api_key).scalar():
                session.add(ApiKey(
                    website=website_name,
                    api_key=api_key,
                    status=validated_result.valid,
                    total=validated_result.total,
                    remaining=validated_result.remaining,
                    last_validated_at=get_now()))
                session.commit()

    @staticmethod
    def update_one(id: int, validated_result: ValidatedResult):
        with DbSession() as session:
            session.query(ApiKey) \
                .filter(ApiKey.id == id) \
                .update({
                    ApiKey.valid: validated_result.valid,
                    ApiKey.total: validated_result.total,
                    ApiKey.remaining: validated_result.remaining,
                    ApiKey.last_validated_at: get_now()})
            session.commit()

    @staticmethod
    def get_all_keys(website_name: str, last_id: int, batch_size: int = 100) -> List[ApiKey]:
        with DbSession() as session:
            return session.query(ApiKey) \
                .filter(ApiKey.id > last_id, ApiKey.website == website_name) \
                .limit(batch_size)

    @staticmethod
    def get_valid_key_count(website_name: str) -> int:
        with DbSession() as session:
            return session.query(ApiKey) \
                .filter(ApiKey.website == website_name, ApiKey.status == ApiKeyStatus.VALID.value) \
                .count()