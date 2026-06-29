from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.auth.router import router as auth_router
from src.admin.router import router as admin_router
from src.owner.router import router as owner_router
from src.cart.router import router as cart_router
from src.orders.router import router as orders_router
from src.products.router import router as products_router
from src.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Antik Marketplace",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(owner_router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(orders_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
