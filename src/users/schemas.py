
from typing import Optional
from pydantic import BaseModel, ConfigDict

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


class Token(BaseModel):
    access_token: str
    token_type: str
