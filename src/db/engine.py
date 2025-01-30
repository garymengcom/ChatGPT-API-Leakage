from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from src.configs import DB_URL

DbEngine = create_engine(DB_URL, pool_pre_ping=True, pool_size=10, pool_recycle=3600)


DbSession = sessionmaker(bind=DbEngine)
Base = declarative_base()
