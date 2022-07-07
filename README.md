# FASTAPI E-Commerce Customer Basket Backend

This code is a basic demonstration of an e-commerce website's backend with basic user interactions. Users can signup, login, increase their balance of their account, add products to their carts, delete those products, and filly purchase them.

The project is yet to have a sophisticated database and I use arrays to keep the user and item data.

## Installation

Use the following command to install the projects' requirements.

```bash
pip install -r requirements.txt
```

## Usage

To use it, just run the following command: 

```bash
uvicorn main:app --reload
```

and open up your browser and navigate to the "127.0.0.1:8000/docs".

## License
[MIT](https://choosealicense.com/licenses/mit/)