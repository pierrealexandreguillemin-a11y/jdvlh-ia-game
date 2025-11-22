import yaml
from pathlib import Path
from sqlalchemy import Column, Float, Integer, String, Text, create_engine
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Chemin absolu vers config.yaml
CONFIG_PATH = Path(__file__).parent.parent / "config" / "config.yaml"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

DB_URL = f"sqlite:///game.db"

engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class GameStateModel(Base):
    __tablename__ = "game_states"

    player_id = Column(String, primary_key=True)
    state_json = Column(JSON)
    last_activity = Column(Float)
    history_length = Column(Integer, default=0)  # For auto-save tracking


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
