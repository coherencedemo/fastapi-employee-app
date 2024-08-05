import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import logging

# Load the .env file (useful for local development)
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use the DATABASE_URL provided by Coherence
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    # If DATABASE_URL is not provided, construct it from individual components
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("EMPLOYEES_HOST") or os.getenv("EMPLOYEES_IP")  # Use EMPLOYEES_HOST or EMPLOYEES_IP
    DB_NAME = os.getenv("DB_NAME")
    DB_PORT = os.getenv("EMPLOYEES_PORT", "5432")  # Default to 5432 if not provided

    SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Log the constructed URL (make sure to mask the password)
masked_url = SQLALCHEMY_DATABASE_URL.replace(DB_PASSWORD, "********") if DB_PASSWORD else SQLALCHEMY_DATABASE_URL
logger.info(f"Database URL: {masked_url}")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()