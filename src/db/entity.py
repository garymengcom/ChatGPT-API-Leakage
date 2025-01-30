import datetime
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy import UniqueConstraint

from src.db.engine import Base, DbEngine
from src.models import ApiKeyStatus


class ApiKey(Base):
    __tablename__ = 'api_keys'

    id = Column(Integer, primary_key=True)

    website = Column(String(20), nullable=False)
    api_key = Column(String(512), nullable=False)
    status = Column(Integer, nullable=False, default=ApiKeyStatus.ADDED.value)
    remaining = Column(Integer, nullable=False, default=0)
    last_validated_at = Column(DateTime, nullable=False, default=datetime.datetime.now, server_default=func.current_timestamp())

    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now, server_default=func.current_timestamp())
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.now, server_default=func.current_timestamp(), onupdate=datetime.datetime.now)

    __table_args__ = (
        UniqueConstraint('website', 'api_key'),
    )

if __name__ == '__main__':
    Base.metadata.create_all(DbEngine)