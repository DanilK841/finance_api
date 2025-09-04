from src.database import Base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime



class TransactionTypes(Base):
    __tablename__ = "transaction_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship('Transactions', back_populates='transaction_types')

# а где и как хранится поле transactions
# на что влияет параметр back_populates. оно должно строго совпадать с названием таблицы с которой устанавливается связь?



