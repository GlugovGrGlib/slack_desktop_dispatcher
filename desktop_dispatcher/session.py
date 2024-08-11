from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL

from desktop_dispatcher.utils import get_env_variable

db_user = get_env_variable("POSTGRES_USER")
db_password = get_env_variable("POSTGRES_PASSWORD")
db_host = get_env_variable("POSTGRES_HOST")
db_name = get_env_variable("POSTGRES_DB")

db_url = URL.create(
        drivername="postgresql",
        database=db_name,
        username=db_user,
        password=db_password,
        host=db_host,
        port=5432
)

engine = create_engine(db_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
