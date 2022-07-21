from tokenize import cookie_re
from fastapi import FastAPI, Form, Depends, Query

from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.encoders import jsonable_encoder
# from fastapi.middleware.cors import CORSMiddleware

from datetime import timedelta

from models import *
from templates import *
from dependancies import *



app = FastAPI()

# origins = [
#     "http://localhost.com",
#     "https://localhost.com",
#     "http://localhost",
#     "http://localhost:8080",
#     "http://localhost:8080/users/me",
#     "http://localhost:8080/login/",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

@app.get('/', tags=['index'])
async def index():
    return HTMLResponse(content=rootResponse)#{'message': 'start', 'a': a}

@app.get('/users/me', response_model=UserRepresentation, tags=['user setup'])
async def user_page(user: User = Depends(getCurrentActiveUser)):
    return user

@app.post("/token", response_model=Token, tags=['user setup'])
async def access_token_end_point(form_data = Depends(OAuth2PasswordRequestForm)):
    user = authenticateUser(users, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    accessToken = createAccessToken(
        data={"sub": user.username}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": accessToken, "token_type": "bearer"}


@app.get('/signup/', tags=['user setup'])
async def load_sign_up_page():
    return HTMLResponse(content=loginResponse)#'message': 'please singup'}

@app.post('/signup/', response_model=UserRepresentation, tags=['user setup'])
async def sign_up(user: SignUpUser):
    if users.get(user.username):
      raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User Already Exists",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = User(**user.dict(), hashedPassword=getPasswordHash(user.password))
    users[user.username] = jsonable_encoder(user)
    return user


## redirect to the main page after this
## try {user.username} instead of /me/
## Note: be carefull about the input of the methods, specifically those who
## have user as the input, we need a rework on the models as well!
@app.put('/users/me/addBalance', response_model=UserRepresentation, tags=['user action'])
async def add_to_customer_balance(amount: int, user: UserRepresentation = Depends(getCurrentUser)):
    user_new = User(**users[user.username])
    user_new.balance += amount
    users[user.username] = jsonable_encoder(user_new)
    # users[user.username]['balance'] = users[user.username]['balance'] + amount
    # user = users[user.username]
    print(user_new)
    return user_new

## Change this so it can have a proper return, also send it back to UI for better presentation
## instead of having a tuple of str and list
@app.get('/users/me/products', response_model=tuple[str, list[BuyableItem]], tags=['user action'])
async def show_customer_basket(user: User = Depends(getCurrentActiveUser)):
    basketTotal = sum([x.price * x.quantity for x in user.cart])
    return f"Basket Total is: {basketTotal}", user.cart


@app.get('/products/', response_model=list[BuyableItem], tags=['products'])
async def show_all_available_products():
    return list(items.values())



@app.put('/users/me/addToBasket', response_model=UserRepresentation, tags=['user action'])
async def add_to_customer_basket(
    quantity: int = 1, 
    item: str = Query('item 1', enum=[x for x in items.keys()]), 
    user: UserRepresentation = Depends(getCurrentUser),
    ):
    
   
    if(not quantity):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="The minimum number that can be in your basket is 1! If you wish to remove it, please refer to the other method",
            headers={"WWW-Authenticate": "Bearer"},
        )

    itemIndex = next((index for (index, product) in enumerate(user.cart) if product.name == item), None)
    
    updatedUserCart = user.copy()
    if itemIndex is not None:
        updatedUserCart.cart[itemIndex].quantity += quantity
    else:
        updatedUserCart.cart.append(Item(**items[item], quantity=quantity))
    
    users[user.username] = jsonable_encoder(updatedUserCart)
    print(users[user.username])
    return updatedUserCart


@app.patch('/users/me/changeProductAmount', response_model=UserRepresentation, tags=['user action'])
async def change_product_quantity_in_customer_basket(
    quantity: int = 1, 
    item: str = Query('item 1', enum=[x for x in items.keys()]),
    user: UserRepresentation = Depends(getCurrentUser)):
    
    if item not in [x.name for x in user.cart]:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="You don't have this product in your basket",
            headers={"WWW-Authenticate": "Bearer"},
        )

    itemIndex = next((index for (index, product) in enumerate(user.cart) if product.name == item), None)
    if itemIndex is None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="You don't have any products in your basket",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if quantity < 1:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="The minimum number that can be in your basket is 1! If you wish to remove it, please refer to the other method",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    updatedUserCart = user.copy()
    updatedUserCart.cart[itemIndex].quantity = quantity
    
    users[user.username] = jsonable_encoder(updatedUserCart)
    return updatedUserCart


@app.delete('/users/me/removeFromBaket', response_model=UserRepresentation, tags=['user action'])
async def remove_product_from_customer_basket(
    item: str = Query('item 1', enum=[x for x in items.keys()]), 
    user: UserRepresentation = Depends(getCurrentUser)):
    
    if item not in items.keys():
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Item doesn't exist",
            headers={"WWW-Authenticate": "Bearer"},
        )

    itemIndex = next((index for (index, product) in enumerate(user.cart) if product.name == item), None)
    if itemIndex is None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="You don't have this product in your basket, so we cannot remove it!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    updatedUserCart = user.copy()
    updatedUserCart.cart.pop(itemIndex)
    
    users[user.username] = jsonable_encoder(updatedUserCart)
    return updatedUserCart


## write a customer handler for when there is not enough balance
## write a customer handler for when the basket is empty
@app.put('/users/me/purchase', response_model=UserRepresentation, tags=['user action'])
async def purchase_items_in_basket(user: UserRepresentation = Depends(getCurrentUser)):
    if user.cart == []:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Basket is empty",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    itemTotalqouta = {x.name: x.quantity * x.price for x in user.cart}
    total = sum(itemTotalqouta.values())
    print(total)

    if total > user.balance:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Balance is not enough",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_new = user.copy()
    user_new.balance, user_new.cart = user.balance-total, []
    users[user.username] = jsonable_encoder(user_new)

    return user_new



@app.get("/login", tags=['user setup'])
async def load_login_webpage():
    return HTMLResponse(content=loginResponse)

# @app.post("/login", tags=['user setup'])
# async def get_chekable_data(
#     request: Request, 
#     user: UserRepresentation = Depends(getCurrentUser)
#     ):
#     data = dict(await request.form())
#     print(data.get('username'))

    # user = authenticateUser(users, data.get('username'), data.get('password'))
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Incorrect username or password",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    # access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # accessToken = createAccessToken(
    #     data={"sub": user.username}, expires_delta=access_token_expires
    # )

    # # response = RedirectResponse(url="/users/me")
    # response = HTMLResponse(content=loginResponse)
    # response.set_cookie(
    #         "Authorization",
    #         value=f"Bearer {jsonable_encoder(accessToken)}",
    #         domain="localtest.com",
    #         httponly=True,
    #         max_age=1800,
    #         expires=1800,
    #     )
    # print(response.headers.get(key='cookie'))
    # return response
    # return user
    
import sys
import time
import uvicorn
import threading
import webbrowser

def start_server(port=8000):
    uvicorn.run(app, port=port, log_level="info", )

if __name__ == "__main__":
    # thread.start_new_thread(start_server,())
    url = 'http://127.0.0.1:8000/docs'

    threading.Thread(target=start_server).start()
    webbrowser.open_new(url)

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            sys.exit(0)
