import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import logging
from urllib.parse import urlparse, urlunparse

# Load the .env file (useful for local development)
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def mask_password(url):
    """Mask the password in the given URL."""
    parsed = urlparse(url)
    if parsed.password:
        masked = parsed._replace(netloc=f"{parsed.username}:{'*' * 8}@{parsed.hostname}")
        return urlunparse(masked)
    return url

# Use the DATABASE_URL provided by Coherence
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    # If DATABASE_URL is not provided, construct it from individual components
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("EMPLOYEES_HOST") or os.getenv("EMPLOYEES_IP")
    DB_NAME = os.getenv("DB_NAME")
    DB_PORT = os.getenv("EMPLOYEES_PORT", "5432")

    # Check if all required components are available
    required_vars = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME"]
    missing = [var for var in required_vars if not locals().get(var)]
    
    if missing:
        error_msg = f"Missing required environment variables: {', '.join(missing)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Ensure the URL uses the postgresql:// scheme
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Log the constructed URL (with masked password)
masked_url = mask_password(SQLALCHEMY_DATABASE_URL)
logger.info(f"Database URL: {masked_url}")

try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except Exception as e:
    logger.error(f"Error creating database engine: {str(e)}")
    raise

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Log all relevant environment variables (for debugging)
env_vars = ["DATABASE_URL", "DB_USER", "EMPLOYEES_HOST", "EMPLOYEES_IP", "DB_NAME", "EMPLOYEES_PORT"]
for var in env_vars:
    value = os.getenv(var)
    if var != "DB_PASSWORD":
        logger.info(f"{var}: {value}")
    else:
        logger.info(f"{var}: {'*' * 8 if value else 'Not set'}")