from typing import List, Annotated

from fastapi import Depends, HTTPException, APIRouter
from requests import Session

from auth.auth import get_current_user
from auth.models import User
from db.database import get_db
from portfolio.model import Portfolio
from portfolio.schemas import PortfolioCreate, PortfolioOut

db_dependency = Annotated[Session, Depends(get_db)]


router = APIRouter(
    prefix="/portfolio",
    tags=["portfolio"],
)

@router.get("/{id}", response_model=PortfolioOut)
def get_portfolio(id: int, db: Session = Depends(get_db)):
    portfolio = db.query(Portfolio).filter(Portfolio.id == id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio entry not found")

    return portfolio

@router.get("/users/", response_model=List[PortfolioOut])
def get_portfolio(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    portfolios = db.query(Portfolio).filter_by(user_id=user.id).all()
    if not portfolios:
        return []
    # all_portfolios = db.query(Portfolio).all()
    # print(all_portfolios)
    # print(db.query(Portfolio).filter_by(user_id=user.id).all())
    return portfolios
@router.post("/", response_model=PortfolioOut)
def create_portfolio(data: PortfolioCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # current_price = fetch_price_for_portfolio(data.coin_id)
    # total_investment = data.quantitive * data.entry_price
    # current_value = data.quantitive * current_price
    # profit_loss = current_value - total_investment

    portfolio = Portfolio(
        coin_id=data.coin_id,
        quantitive=data.quantitive,
        entry_price=data.entry_price,
        profit_loss=data.profit_loss,
        user_id = user.id
    )

    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)

    return portfolio