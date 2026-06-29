from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: bool
    app_name: str


class HealthCheckHealthResponse(BaseModel):
    item: HealthResponse | None
