from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from transaction_types.schemas import TransactionTypesResponse
from users.schemas import UserResponse


class TransactionBase(BaseModel):
    amount: Decimal = Field(gt=0)
    category: str
    status: str

class TransactionCreate(TransactionBase):
    user_id: int
    type_id: int

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    type_id: int
    user: UserResponse
    transaction_types: TransactionTypesResponse

    model_config = ConfigDict(from_attributes=True)

class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = None
    category: Optional[str] = None
    status: Optional[str] = None
    type_id: Optional[int] = None


class UserTransactions(UserResponse):
    transactions: List[TransactionResponse] = []
########################################################################################