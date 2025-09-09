from typing import Optional
from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

# позволяет создавать объект на основе объекта из бд?

class UserCreate(BaseModel):
    name: str
    password: str
    email: str
class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
