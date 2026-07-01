from pydantic import BaseModel


class OutageResponse(BaseModel):
    id: int
    date_time: str
    reachability_state: str
    last_connection_test: str
    change_state: str
    test_target_type: str
    start_time: str | None
    end_time: str | None
    duration_sec: float | None
    started_group_id: int | None
    ended_group_id: int | None


class OutageListResponse(BaseModel):
    items: list[OutageResponse | None] | None
