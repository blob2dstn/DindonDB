

from datetime import datetime
import enum
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from cogs.pvp.db import Base


class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, nullable=False)
    elo = Column(Integer, default=1000)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    
    async def calculate_duel(self, opponent_elo, outcome):
        k_factor = 32
        expected_score = 1 / (1 + 10 ** ((opponent_elo - self.elo) / 400))
        if outcome == "win":
            score = 1
            self.wins += 1
        elif outcome == "loss":
            score = 0
            self.losses += 1
        else:
            score = 0.5
        self.elo += k_factor * (score - expected_score)
        
    
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