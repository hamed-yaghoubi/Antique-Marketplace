from fastapi import FastAPI

from src.auth.router import router as auth_router
from src.cart.router import router as cart_router
from src.orders.router import router as orders_router
from src.products.router import router as products_router
from src.admin.router import router as admin_router

app = FastAPI(
    title="Antik Marketplace",
    version="1.0.0"
)

from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(auth_router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(admin_router)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
