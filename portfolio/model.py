from db.database import Base
from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, text, ForeignKey
from sqlalchemy.orm import relationship


class Portfolio(Base):
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True, index=True)
    coin_id = Column(String, nullable=False)
    quantitive = Column(Integer, nullable=False)
    entry_price = Column(Float, nullable=False)
    profit_loss = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="portfolios")