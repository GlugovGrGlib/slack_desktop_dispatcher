import asyncio
from logging.config import fileConfig

from sqlalchemy import URL, pool, text, exc
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config, create_async_engine

from alembic import context

from desktop_dispatcher.models import * #noqa: F403
from desktop_dispatcher.session import Base  # noqa: E402
from desktop_dispatcher.config import get_env_variable  # noqa: E402


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

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

custom_value = context.config.get_main_option("sqlalchemy.url", db_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata


target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

async def create_db_if_not_exists():
    """
    Create database if it does not exist.
    """
    database = db_name  # Ensure db_name is defined
    db_postgres = URL.create(
        drivername="postgresql",
        database="postgres",  # Connect to 'postgres' database first
        username=db_user,     # Ensure db_user is defined
        password=db_password, # Ensure db_password is defined
        host=db_host,         # Ensure db_host is defined
        port=5432             # Assuming the default PostgreSQL port
    )
    
    try:
        engine = create_async_engine(db_url)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            print(f'Database {database} already exists.')
    except exc.OperationalError:
        # Handle the case where the database does not exist
        print(f'Database {database} does not exist. Creating now.')

        # Connect to the 'postgres' database to create the new database
        engine = create_async_engine(db_postgres)
        async with engine.connect() as conn:
            await conn.execution_options(isolation_level="AUTOCOMMIT").execute(
                text(f'CREATE DATABASE {database};')
            )
            print(f'Database {database} created.')

        engine = create_async_engine(db_url)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            print(f'Successfully connected to the new database {database}.')


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
