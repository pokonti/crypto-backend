from datetime import datetime

from pydantic import BaseModel, field_serializer


class PortfolioCreate(BaseModel):
    coin_id: str
    quantitive: int
    entry_price: float
    profit_loss: float


class PortfolioOut(BaseModel):
    id: int
    coin_id: str
    quantitive: float
    entry_price: float
    profit_loss: float
    created_at: datetime

    @field_serializer("created_at")
    def format_created_at(self, dt: datetime, _info):
        return dt.strftime("%d-%m-%Y")
