
from fastapi import FastAPI, Depends, status

from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException

from fastapi.encoders import jsonable_encoder
from datetime import datetime, timedelta

# import utils
from crud.cruds import *
from model.models import *

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"# "e1d69c39d71f9fd11381fcfc0af4c01314d8c6d7f93740f89e62a707cfbc0ffd"#
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 2

users = {
    'johndoe': 'secret'
}

usersCart = {
    'johndoe': {
          'username': 'johndoe',
          'cart' : [{
            'name': "item 1",
            "price": 12.5,
            'quantity': 2
          }, 
          {
            'name': "item 2",
            "price": 7.5,
            'quantity': 4
          }]
    }
}

items = {
    'item 1': {
      'name': "item 1",
      "price": 12.5
    },
    'item 2': {
      'name': "item 2",
      "price": 7.5
    },
    'item 3': {
      'name': "item 3",
      "price": 15.7
    } 
}


manager = LoginManager(
    secret=SECRET_KEY, token_url='/login',
    use_cookie=True,
    custom_exception=NotAuthenticatedException,
)

@manager.user_loader()
def query_user(username: str):
    """
    Get a user from the db
    :param user_id: E-Mail of the user
    :return: None or the user object
    """
    return UserData(username=username, hashed_password=users.get(username))



app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='templates')


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    'https://i.imgur.com/oYiTqum.jpg'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(NotAuthenticatedException)
def auth_exception_handler(request: Request, exc: NotAuthenticatedException):
    return RedirectResponse(url='/login')



@app.get('/', tags=['index'])
async def index_wenpage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", tags=['user setup'])
async def login_webpage(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", tags=['user setup'])
async def login(user: OAuth2PasswordRequestForm = Depends()):
  
    if not users.get(user.username):
        RedirectResponse(url="/login", status_code=status.HTTP_404_NOT_FOUND)
        #raise InvalidCredentialsException
    elif user.password != users[user.username]:
        RedirectResponse(url="/login", status_code=status.HTTP_404_NOT_FOUND)
        #raise InvalidCredentialsException

    token = manager.create_access_token(
        data=dict(sub=user.username),
        expires=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response = RedirectResponse(url=f"/user/{user.username}", status_code=status.HTTP_302_FOUND)
    manager.set_cookie(response, token)
    return response
    # return {'access_token': access_token}


@app.get('/logout', response_class=HTMLResponse)
async def logout(request: Request, user=Depends(manager)):
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    manager.set_cookie(response, "")
    return response


@app.get("/signup", tags=['user setup'])
async def signup_webpage(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request, "error": ""})

@app.post("/signup", tags=['user setup'])
async def signup_webpage(request: Request):
    newUser = dict(await request.form())
    if newUser.get('username') in users:
      return templates.TemplateResponse("signup.html", {"request": request, "error": ["This Username Is Already Taken"]})
    elif newUser.get('password') != newUser.get('repeat_password'):
      return templates.TemplateResponse("signup.html", {"request": request, "error": ["The Passwords Don't Match"]})
    # UserData(username=newUser['username'], hashed_password=newUser['password'])
    else:  
      users[newUser['username']] = newUser['password']
      user = User(username=newUser['username']).dict()
      user['cart'] = []
      usersCart[newUser['username']] = UserDashboard(**user).dict()

      token = manager.create_access_token(
          data=dict(sub=newUser['username']),
          expires=timedelta(minutes=1)
      )
      response = RedirectResponse(url=f"/user/{newUser['username']}", status_code=status.HTTP_302_FOUND)
      manager.set_cookie(response, token)
      return response


async def getBasicData(user=Depends(manager)):
    return User(username=user.username)

@app.get('/user/{me}', response_class=HTMLResponse, )
async def dashboard(request: Request, me:str, user: User = Depends(getBasicData)):
  if me != user.username:
    return RedirectResponse(url=f'/user/{user.username}')
  return templates.TemplateResponse("user_page.html", {"request": request, 'name': user.username})


@app.get('/user/{me}/cart', response_class=HTMLResponse)
async def user_cart_items(request: Request, me:str, user=Depends(manager)):
  if me != user.username:
    return RedirectResponse(url=f'/user/{user.username}/cart')
  user = UserDashboard(**usersCart.get(user.username))
  total = sum([x.price * x.quantity for x in user.cart])
  return templates.TemplateResponse("user_cart_items.html", {"request": request, 'cart': user.cart, "total": total, 'name': user.username, 'error': None})


@app.post('/update/{item}')
async def update_cart(request: Request, item:str, user=Depends(getBasicData)):
  
  udpate_request = dict(await request.form()).get(item)
  user = UserDashboard(**usersCart.get(user.username))
  if(udpate_request is None):
    return templates.TemplateResponse("user_cart_items.html", 
                                        {"request": request, 
                                        'cart': user.cart, 
                                        'name': user.username, 
                                        'error': 'Please choose an amount!'})

  if(not udpate_request.isnumeric()):
    return templates.TemplateResponse("user_cart_items.html", 
                                        {"request": request, 
                                        'cart': user.cart, 
                                        'name': user.username, 
                                        'error': 'Please choose a valid amount!'})
  
  usercart = UserDashboard(**usersCart.get(user.username))
  for product in usercart.cart:
    if product.name == item:
      product.quantity = int(udpate_request)
  usersCart.get(user.username).update(cart = jsonable_encoder(usercart.cart))

  return RedirectResponse(url=f'/user/{user.username}/cart', status_code=status.HTTP_302_FOUND)




@app.get("/products", tags=['user setup'])
async def login_webpage(request: Request, user=Depends(getBasicData)):
    return templates.TemplateResponse("products_page.html", {"request": request, 'items': items.values(), 'user': user.username})

@app.post("/addToCart/{item}", tags=['user setup'])
async def add_to_cart(request: Request, item:str, user=Depends(getBasicData)):
  if(item not in items.keys()):
    return templates.TemplateResponse("products_page.html", 
                                        {"request": request, 
                                        'items': items.values(),
                                        'user': user.username,
                                        'error': 'Please try again, something went wrong'})

  
  usercart = UserDashboard(**usersCart.get(user.username))
  if usercart.cart == []:
    usercart.cart.append(CartItem(**items.get(item)))
  elif item in [x.name for x in usercart.cart]:
    itemIndex = [x.name for x in usercart.cart].index(item)
    usercart.cart[itemIndex].quantity += 1
  elif item not in [x.name for x in usercart.cart]:
    usercart.cart.append(CartItem(**items.get(item)))
    
  usersCart.get(user.username).update(cart = jsonable_encoder(usercart.cart))
  return templates.TemplateResponse("products_page.html", {"request": request, 'items': items.values(), 'user': user.username})


@app.post("/user/{me}/purchase", tags=['user setup'])
async def login_webpage(request: Request, me: str, user=Depends(getBasicData)):
  if me != user.username:
    return RedirectResponse(url=f'/user/{user.username}/cart')
  
  usersCart.get(user.username).update(cart=[])
  return RedirectResponse(url=f'/user/{user.username}', status_code=status.HTTP_302_FOUND)
