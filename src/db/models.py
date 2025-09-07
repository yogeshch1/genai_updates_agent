# src/db/models.py
import os
import uuid
import datetime
from sqlalchemy import create_engine, Column, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/genai")

Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String, nullable=False, index=True)
    source_id = Column(String, nullable=False, index=True, unique=True)
    title = Column(Text)
    authors = Column(JSON)
    abstract = Column(Text)
    url = Column(Text)
    categories = Column(JSON)
    published_date = Column(DateTime)
    raw = Column(JSON)
    inserted_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

def get_engine(db_url: str = None):
    db_url = db_url or os.environ.get("DATABASE_URL", DATABASE_URL)
    engine = create_engine(db_url, pool_pre_ping=True)
    return engine

def get_session(engine=None):
    engine = engine or get_engine()
    Session = sessionmaker(bind=engine)
    return Session()
