from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

DB_URL = f"sqlite:///{Path(__file__).parent / 'app.db'}"
engine = create_engine(DB_URL, echo=False)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)
