from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str
    database_connected: bool
    timestamp: str


class ErrorResponse(BaseModel):
    error: str
    detail: str
