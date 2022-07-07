from pydantic import BaseModel

from typing import Any, Callable, Generator, Type, TypeVar, ClassVar, Generic


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class PresentableItem(BaseModel):
    name: str
    price: float


class BuyableItem(PresentableItem):
    quantity: int = 1


class Item(BuyableItem):
    id: int


class Guest(BaseModel):
    name: str
    username: str
    email: str
    balance: float = 0

## This is inefficient, create a cookie for each user to 
## store their cart items
class UserRepresentation(Guest):
    cart: list[BuyableItem] = []


class SignUpUser(Guest):
    password: str
    repeatPassword: str | None = None


class User(UserRepresentation):
    hashedPassword: str
    

# T = TypeVar("T")
# class StrictType(Generic[T]):
#     type_: ClassVar[Type[T]]
#     def __get_validators__(cls) -> Generator[Callable[[Any], int], None, None]:
#         # yield int_validator
#         yield cls.validate

#     @classmethod
#     def validate(cls, v: Any) -> int:
#         if not isinstance(v, cls.type_):
#             raise TypeError(f"Received {type(v)}; required {cls.type_}")
#         return v

# class StrictInt(StrictType[int]):
#     type_ = int


   
users: dict = {
    'johndoe': {
        "name": "John Doe",
        "username": "johndoe",
        "email": "johndoe@example.com",
        "hashedPassword": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "balance": 20, 
        "cart": [],
    }
}


items: dict = {
    'item 1': {
        'id': 1,
        'name': 'item 1',
        'price': 10.5
    },
    'item 2': {
        'id': 2,
        'name': 'item 2',
        'price': 15
    },
    'item 3': {
        'id': 3,
        'name': 'item 3',
        'price': 12.99
    },
    'item 4': {
        'id': 4,
        'name': 'item 4',
        'price': 23.25
    },
}