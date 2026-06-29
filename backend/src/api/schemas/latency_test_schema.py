from pydantic import BaseModel


class LatencyTestResponse(BaseModel):
    id: int
    group_id: int
    date_time: str
    target: str
    test_target_type: str
    success: bool
    latency_ms: float | None
    error_message: str | None


class LatencyTestListResponse(BaseModel):
    items: list[LatencyTestResponse | None] | None
