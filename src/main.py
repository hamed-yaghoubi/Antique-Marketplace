import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import DataError, IntegrityError

from src.auth.router import router as auth_router
from src.admin.router import router as admin_router
from src.owner.router import router as owner_router
from src.cart.router import router as cart_router
from src.orders.router import router as orders_router
from src.products.router import router as products_router
from src.core.config import get_settings
from src.core.exceptions import AppException, ValidationError

settings = get_settings()

app = FastAPI(
    title="Antik Marketplace",
    version="1.0.0"
)

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


def error_response(status_code: int, code: str, message: str, details=None):
    body = {"success": False, "error": {"code": code, "message": message}}
    if details is not None:
        body["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=body)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return error_response(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        loc = " -> ".join(str(l) for l in error.get("loc", []))
        errors.append({"field": loc, "message": error.get("msg", "Validation error")})
    return error_response(
        status_code=422,
        code="VALIDATION_ERROR",
        message="Request validation failed",
        details=errors,
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return error_response(
        status_code=exc.status_code,
        code="HTTP_ERROR",
        message=str(exc.detail),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return error_response(
        status_code=500,
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred",
    )


@app.exception_handler(DataError)
async def data_error_handler(request: Request, exc: DataError):
    orig = getattr(exc, "orig", None)
    detail = str(orig) if orig else str(exc)
    if "numeric field overflow" in detail.lower():
        return error_response(
            status_code=422,
            code="NUMERIC_OVERFLOW",
            message="Value exceeds the maximum allowed for this field",
        )
    return error_response(
        status_code=422,
        code="DATA_ERROR",
        message="Invalid data provided",
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return error_response(
        status_code=409,
        code="INTEGRITY_ERROR",
        message="The request conflicts with existing data",
    )


app.include_router(auth_router)
app.include_router(owner_router)
app.include_router(admin_router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(orders_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)
