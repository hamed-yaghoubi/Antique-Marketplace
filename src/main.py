from fastapi import FastAPI

from src.auth.router import router as auth_router
from src.cart.router import router as cart_router
from src.orders.router import router as orders_router
from src.products.router import router as products_router

app = FastAPI(
    title="Antik Marketplace",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(orders_router)
