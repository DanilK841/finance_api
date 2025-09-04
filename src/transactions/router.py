from datetime import datetime
from http.client import HTTPException
from typing_extensions import Annotated, Optional

from fastapi import APIRouter, Depends
from sqlalchemy import update
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import select, update, delete

from transaction_types.models import TransactionTypes
from transactions.models import Transactions
from transactions.schemas import TransactionResponse, TransactionCreate, UserTransactions, TransactionUpdate
from users.schemas import UserResponse
from database import get_db
from users.models import Users

from users.router import get_current_user

router = APIRouter(prefix='/transaction', tags=['ТРАНЗАКЦИИ'])

@router.post("/trans/", response_model=TransactionResponse)
async def create_transaction(trans: TransactionCreate, session: Session = Depends(get_db)):
    user = session.get(Users, trans.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    trans_type = session.get(TransactionTypes, trans.type_id)
    if not trans_type:
        raise HTTPException(status_code=404, detail="Type transactions not found")

    db_trans = Transactions(**trans.dict())
    session.add(db_trans)
    await session.commit()
    await session.refresh(db_trans)
    return db_trans

@router.get("/user_transactions/{user_id}", response_model=UserTransactions)
async def get_user_trans(current_user: Annotated[Users, Depends(get_current_user)], user_id: int, session: Session = Depends(get_db)):
    # db_user = session.query(Users).options(joinedload(Users.transactions)).filter(Users.id == user_id).first()
    db_user_transactions_stmt = await session.execute(select(Users)
                                                    .where(Users.id == user_id)
                                                    .options(selectinload(Users.transactions)  # Загружаем транзакции
                                                    .selectinload(Transactions.transaction_types)  # И их типы
                                                    )
                                                      )
    db_user_transactions = db_user_transactions_stmt.unique().scalar_one_or_none()
    if not db_user_transactions:
        raise HTTPException(status_code=404, detail="User not found")
    return UserTransactions.model_validate(db_user_transactions)

@router.get("/{trans_id}", response_model=TransactionResponse)
async def get_trans(current_user: Annotated[Users, Depends(get_current_user)], trans_id: int, session: Session = Depends(get_db)):
    # db_user = session.query(Users).options(joinedload(Users.transactions)).filter(Users.id == user_id).first()
    result = await session.execute(select(Transactions).where(Transactions.id == trans_id).options(selectinload(Transactions.transaction_types)))
    db_trans = result.scalar_one_or_none()
    return db_trans

# @router.put("/transactions/{trans_id}", response_model=TransactionResponse)
# def update_trans(current_user: Annotated[Users, Depends(get_current_user)], trans_id: int, trans: TransactionUpdate, session: Session = Depends(get_db)):
#     db_trans = session.select(Transactions).filter(Transactions.id == trans_id).first()
#     amount = trans.amount if trans.amount else db_trans.amount
#     if amount < 0:
#         raise HTTPException(status_code=404, detail="Amount must be greater than 0")
#     category = trans.category if trans.category else db_trans.category
#     status = trans.status if trans.status else db_trans.status
#     type_id = trans.type_id if trans.type_id else db_trans.type_id
#     trans_type = session.query(TransactionTypes).filter(TransactionTypes.id == type_id).first()
#     if not trans_type:
#         raise HTTPException(status_code=404, detail="Type transactions not found")
#
#
#     update_stmt = update(Transactions).where(Transactions.id == trans_id).values(
#         amount=amount,
#         category=category,
#         status=status,
#         type_id=type_id
#     )
#     session.execute(update_stmt)
#     session.commit()
#     session.refresh(db_trans)
#     return db_trans

@router.delete("/transactions/{trans_id}")
def delete_trans(trans_id: int, session: Session = Depends(get_db)):
    db_trans = session.query(Transactions).filter(Transactions.id == trans_id).first()
    # db_trans = Transactions.query.get_or_404(trans_id)
    session.delete(db_trans)
    session.commit()
    return {"msg":f"Delete transaction with id {trans_id} succes"}