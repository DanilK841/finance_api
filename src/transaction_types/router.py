from http.client import HTTPException

from fastapi import APIRouter, Depends
from sqlalchemy import update
from sqlalchemy.orm import Session
from typing import List

from src.transaction_types.models import TransactionTypes
from src.transaction_types.schemas import TransactionTypesResponse, TransactionTypesCreate, TransactionTypesUpdate
from src.database import get_db
from src.transactions.models import Transactions

router = APIRouter(prefix='/transaction_types', tags=['ТИПЫ ТРАНЗАКЦИЙ'])

@router.post("/", response_model=TransactionTypesResponse)
async def create_tr_types(trtypes: TransactionTypesCreate, session: Session = Depends(get_db)):
    db_trtypes = TransactionTypes(
        name=trtypes.name,
        description=trtypes.description
    )
    session.add(db_trtypes)
    await session.commit()
    await session.refresh(db_trtypes)
    return db_trtypes

@router.put("/{update_id}", response_model=TransactionTypesResponse)
def update_tr_types(update_id: int, trtypes: TransactionTypesUpdate, session: Session = Depends(get_db)):
    db_trtypes = session.query(TransactionTypes).filter(TransactionTypes.id == update_id).first()
    name = trtypes.name if trtypes.name else db_trtypes.name
    description = trtypes.description if trtypes.description else db_trtypes.description

    updt_stmt = update(TransactionTypes).where(TransactionTypes.id == update_id).values(
        name=name,
        description=description
    )
    session.execute(updt_stmt)
    session.commit()
    session.refresh(db_trtypes)
    return db_trtypes

@router.get("/", response_model=List[TransactionTypesResponse])
def get_all_types(session: Session = Depends(get_db)):
    db_trtypes = session.query(TransactionTypes).all()
    return db_trtypes

@router.get("/{id}", response_model=TransactionTypesResponse)
def get_all_types(id: int, session: Session = Depends(get_db)):
    db_trtypes = session.query(TransactionTypes).filter(TransactionTypes.id == id).first()
    return db_trtypes

@router.delete("/{trans_t_id}")
def delete_trans(trans_t_id: int, session: Session = Depends(get_db)):
    db_trans = session.query(Transactions).filter(Transactions.type_id == trans_t_id)
    if db_trans:
        HTTPException(status_code=404, detail="Exist transactions with this transaction_types")

    db_trans_type = session.query(TransactionTypes).filter(TransactionTypes.id == trans_t_id).first()
    session.delete(db_trans_type)
    session.commit()
    return {"msg": f"Delete transaction type with name {db_trans_type.name} succes"}