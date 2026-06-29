from pydantic import BaseModel


class LogResponse(BaseModel):
    id: int
    date_time: str
    log_level: str
    log_type: str
    log_message: str
    class_name: str
    function_name: str
    related_object_type: str | None
    related_object_id: int | None
    details_json: str | None


class LatestLogsResponse(BaseModel):
    items: list[LogResponse | None] | None
