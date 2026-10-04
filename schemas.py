from pydantic import BaseModel, ConfigDict, Field

from models import Role


# ---------- Auth / Users ----------
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=72)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    role: Role


class RoleUpdate(BaseModel):
    role: Role


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Items ----------
class ItemBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    price: float = Field(gt=0)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    """All fields optional so PATCH-style partial updates work."""
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    price: float | None = Field(default=None, gt=0)


class ItemOut(ItemBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    owner_id: int
