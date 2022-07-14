from lib2to3.pytree import Base
from uuid import UUID, uuid4
from pydantic import BaseModel, EmailStr

class NotAuthenticatedException(Exception):
    pass

class ShelfItem(BaseModel):
    name: str
    price: float

class CartItem(ShelfItem):
    quantity: int = 1

# change it when including the database to have a uique ID
class Item(CartItem):
    __id: int = 123#: UUID = uuid4()

class User(BaseModel):
    email: str | None = None
    username: str

class SingUpUser(User):
    signUpPassword: str


class UserDashboard(User):
    cart: list[CartItem]


class UserData(User):
    __id: int = 123#: UUID = uuid4()
    hashed_password: str