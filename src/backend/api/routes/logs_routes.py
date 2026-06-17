from fastapi import APIRouter, Request, Query
from backend.api.api_context import ApiContext
from backend.database.log_entry_repository import LogEntryRepository
from backend.models.models import LogEntry, LogType, LogLevel
from typing import Any

router = APIRouter(prefix="/api/logs")


@router.get("/latest")
def get_latest(
    request: Request,
    limit: int = Query(default=100, ge=1, le=1000),
    log_type: list[LogType] | None = Query(default=None),
    log_level: list[LogLevel] | None = Query(default=None),
) -> list[dict[str, Any]]:
    api_context: ApiContext = request.app.state.api_context

    repository: LogEntryRepository = api_context.log_entry_repository

    if log_type is None:
        log_type = [LogType.SYSTEM]

    if log_level is None:
        log_level = [LogLevel.INFO]

    log_entries: list[LogEntry] = repository.load_latest_list(limit, log_type, log_level)

    if len(log_entries) == 0:
        return [{"logs": None}]

    result: list[dict[str, Any]] = []

    for entry in log_entries:
        result.append(
            {
                "id": entry.id,
                "date_time": entry.date_time,
                "log_level": entry.log_level,
                "log_type": entry.log_type,
                "log_message": entry.log_message,
                "class_name": entry.class_name,
                "function_name": entry.function_name,
                "related_object_type": entry.related_object_type,
                "related_object_id": entry.related_object_id,
                "details_json": entry.details_json,
            }
        )

    return result
