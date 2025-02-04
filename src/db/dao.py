from typing import List

from src.db.engine import DbSession
from src.db.entity import ApiKey
from src.core.logging_utils import get_now
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
                        last_validated_at=get_now(),
                        created_at=get_now(),
                        updated_at=get_now()
                    ))
            session.commit()

    @staticmethod
    def update_one(id: int, validated_result: ValidatedResult):
        with DbSession() as session:
            session.query(ApiKey) \
                .filter(ApiKey.id == id) \
                .update({
                    ApiKey.status: validated_result.status.value,
                    ApiKey.total: validated_result.total,
                    ApiKey.remaining: validated_result.remaining,
                    ApiKey.last_validated_at: get_now(),
                    ApiKey.updated_at: get_now(),
            })
            session.commit()

    @staticmethod
    def get_all_keys(website_name: str, last_id: int, batch_size: int = 10) -> List[ApiKey]:
        with DbSession() as session:
            return session.query(ApiKey) \
                .filter(ApiKey.id > last_id, ApiKey.website == website_name) \
                .order_by(ApiKey.id.asc()) \
                .limit(batch_size)\
                .all()

    @staticmethod
    def get_valid_key_count(website_name: str) -> int:
        with DbSession() as session:
            return session.query(ApiKey) \
                .filter(ApiKey.website == website_name, ApiKey.status == ApiKeyStatus.VALID.value) \
                .count()