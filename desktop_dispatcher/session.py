from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from .config import get_env_variable


db_user = get_env_variable("POSTGRES_USER")
db_password = get_env_variable("POSTGRES_PASSWORD")
db_host = get_env_variable("POSTGRES_HOST")
db_name = get_env_variable("POSTGRES_DB")

db_url = URL.create(
        drivername="postgresql+asyncpg",
        database=db_name,
        username=db_user,
        password=db_password,
        host=db_host,
        port=5432
)

engine = create_async_engine(db_url)

async_session = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()