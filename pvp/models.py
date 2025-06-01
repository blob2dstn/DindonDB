

from datetime import datetime
import enum
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from db import Base


class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    elo = Column(Integer, default=1000)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    
class DuelStatusEnum(enum.Enum):
        waiting = "En attente de joueur",
        in_progress = "En cours",
        validated =  "Validé",
        canceled = "Annulé"
class Duel(Base):
    __tablename__ = "duels"
    
    id = Column(Integer, primary_key=True, index=True)
    player1_id = Column(String, ForeignKey('players.id'))
    player2_id = Column(String, ForeignKey('players.id'))
    winner_id = Column(String, ForeignKey('players.id'), nullable=True)
    status = Column(Enum(DuelStatusEnum), nullable=False, default=DuelStatusEnum.waiting.value)
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_update = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)