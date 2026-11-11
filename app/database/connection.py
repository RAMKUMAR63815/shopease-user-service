from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


# Build the MySQL connection URL safely
DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=settings.db_user,
    password=settings.db_password.get_secret_value(), #get_secret_value() extracts the actual password.
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
)


# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)


# Create a reusable database session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# Base class for all SQLAlchemy database models
Base = declarative_base()


# Provide a database session to FastAPI endpoints
def get_db():
    db = SessionLocal()

    try:
        yield db

    except Exception:
        # Roll back unfinished database changes if an error occurs
        db.rollback()
        raise

    finally:
        # Always close the database session
        db.close()
