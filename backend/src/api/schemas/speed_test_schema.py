from pydantic import BaseModel


class SpeedTestResponse(BaseModel):
    id: int
    date_time: str
    success: bool
    download_mbps: float | None
    upload_mbps: float | None
    ping_ms: float | None
    jitter_ms: float | None
    server_name: str | None
    server_location: str | None
    server_id: int | None
    server_url: str | None
    isp: str | None
    external_ip: str | None
    error_message: str | None
    duration_sec: float | None
    tool: str


class SpeedTestListResponse(BaseModel):
    items: list[SpeedTestResponse | None] | None
