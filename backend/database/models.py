from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

class Portfolio(Base):
    __tablename__ = 'portfolios'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class PortfolioPosition(Base):
    __tablename__ = 'portfolio_positions'
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, nullable=False)
    ticker = Column(String(20), nullable=False)
    quantity = Column(Float, nullable=False)
    average_cost = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
