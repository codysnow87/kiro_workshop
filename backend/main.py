import os
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from mangum import Mangum
from routers import events

# Initialize FastAPI application
app = FastAPI(title="Event Management API")

# Include routers
app.include_router(events.router)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with 422 status and detailed error messages"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)}
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)}
    )


@app.get("/")
def read_root():
    return {"message": "Event Management API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Lambda handler using Mangum adapter
handler = Mangum(app)
