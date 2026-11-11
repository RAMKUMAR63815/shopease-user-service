
from logging.config import fileConfig

from alembic import context

from app.database.connection import Base, DATABASE_URL, engine

# Import model files so SQLAlchemy registers their tables
from app.models import user_model
from app.models import address_model


# Read Alembic configuration
config = context.config

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Get SQLAlchemy model metadata
target_metadata = Base.metadata


# Run migrations without connecting to the database
def run_migrations_offline():

    url = DATABASE_URL.render_as_string(hide_password=False)

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# Run migrations with a live database connection
def run_migrations_online():

    with engine.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# Select migration mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
