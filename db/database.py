import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from environment variable or use SQLite as fallback
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./notifications.db")
logger.info(f"Database URL type: {DATABASE_URL.split(':')[0]}")

# Handle special case for PostgreSQL URLs from Render
if DATABASE_URL.startswith("postgres://"):
    logger.info("Converting postgres:// to postgresql://")
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

try:
    # Create SQLAlchemy engine with appropriate connect_args
    connect_args = {}
    if DATABASE_URL.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        
    engine = create_engine(
        DATABASE_URL, 
        connect_args=connect_args,
        pool_pre_ping=True  # This helps with connection issues
    )
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Test the connection
    with engine.connect() as conn:
        logger.info("Database connection successful")
        
except Exception as e:
    logger.error(f"Database connection error: {e}")
    # Fallback to SQLite if there's an error
    fallback_url = "sqlite:///./notifications.db"
    logger.info(f"Falling back to SQLite: {fallback_url}")
    engine = create_engine(fallback_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import Base from models
from .models import Base

# Create all tables
def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")