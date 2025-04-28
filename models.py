from pydantic import BaseModel


class Crypto(BaseModel):
    id: str
    logo: str
    name: str
    symbol: str
    price_dollars: float
    price_euros: float
    change_24h: float


class PromptRequest(BaseModel):
    prompt: str


class CryptoInfo(BaseModel):
    description: str
    whitepaper: str
    price_change_percentage_24h: float
    price_change_percentage_7d: float
    price_change_percentage_14d: float
    price_change_percentage_30d: float
    price_change_percentage_60d: float
    price_change_percentage_200d: float
    price_change_percentage_1y: float