from typing import Optional
from pydantic import BaseModel, ConfigDict

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
