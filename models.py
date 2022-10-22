from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PlayerScore(Base):
    __tablename__ = 'player_scores'
    id = Column(Integer, primary_key=True, autoincrement=True)
    player = Column(String(255), nullable=False)
    score = Column(Integer, nullable=False)