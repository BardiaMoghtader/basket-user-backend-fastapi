from fastapi import Depends, HTTPException, status, Query
import fastapi

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.openapi.models import OAuthFlow
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, OAuth2
from fastapi.security.utils import get_authorization_scheme_param


from starlette.requests import Request

from models import * 

from datetime import datetime, timedelta

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"# "e1d69c39d71f9fd11381fcfc0af4c01314d8c6d7f93740f89e62a707cfbc0ffd"#
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# class OAuth2PasswordBearerCookie(OAuth2):
#     def __init__(
#         self,
#         tokenUrl: str,
#         scheme_name: str = None,
#         scopes: dict = None,
#         auto_error: bool = True,
#     ):
#         if not scopes:
#             scopes = {}
#         flows = OAuthFlow(password={"tokenUrl": tokenUrl, "scopes": scopes})
#         super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

#     async def __call__(self, request: Request) -> str:
#         header_authorization: str = request.headers.get("Authorization")
#         cookie_authorization: str = request.cookies.get("Authorization")

#         header_scheme, header_param = get_authorization_scheme_param(header_authorization)
#         cookie_scheme, cookie_param = get_authorization_scheme_param(cookie_authorization)

#         authorization = False
#         if header_scheme.lower() == "bearer":
#             authorization = True
#             scheme = header_scheme
#             param = header_param

#         elif cookie_scheme.lower() == "bearer":
#             authorization = True
#             scheme = cookie_scheme
#             param = cookie_param


#         if not authorization or scheme.lower() != "bearer":
#             if self.auto_error:
#                 raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated")
#             else:
#                 return None
#         return param


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# oauth2_scheme = OAuth2PasswordBearerCookie(tokenUrl="login")


def getUser(db, username: str):
    if username in db:
        # user_dict = db[username]
        return User(**db[username])


async def getCurrentUser(token: str = Depends(oauth2_scheme)):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = getUser(users, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def getCurrentActiveUser(user: User = Depends(getCurrentUser)):
    # if user.disabled:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return user


def verifyPassword(plain_password, hashedPassword):
    return pwd_context.verify(plain_password, hashedPassword)


def getPasswordHash(password):
    return pwd_context.hash(password)


def authenticateUser(db, username: str, password: str):
    user = getUser(db, username)
    if not user:
        return False
    if not verifyPassword(password, user.hashedPassword):
        return False
    return user


def createAccessToken(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def getCurrentActiveUsersCart(user: User = Depends(getCurrentUser)):
    return [x.name for x in user.cart]

async def getCurrentActiveUsersFirstCartItem(user: User = Depends(getCurrentUser)):
    return user.cart[0].name if user.cart != [] else ''