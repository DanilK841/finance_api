from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

########################################################################################
class UserResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

# позволяет создавать объект на основе объекта из бд?

class UserCreate(BaseModel):
    name: str
    password: str
class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None


########################################################################################
class TransactionTypesResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class TransactionTypesCreate(BaseModel):
    name: str
    description: Optional[str] = None

class TransactionTypesUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
########################################################################################

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