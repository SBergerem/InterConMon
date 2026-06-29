from pydantic import BaseModel
from api.schemas.latency_test_schema import LatencyTestResponse


class LatencyTestGroupResponse(BaseModel):
    id: int
    start_time: str
    end_time: str
    time_needed_sec: float
    any_success: bool
    group_success: bool
    test_target_type: str
    tests: list[LatencyTestResponse | None] | None


class LatencyTestGroupListResponse(BaseModel):
    items: list[LatencyTestGroupResponse | None] | None
