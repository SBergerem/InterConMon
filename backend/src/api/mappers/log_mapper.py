from models.models import LogEntry
from api.schemas.log_schema import LogResponse, LatestLogsResponse


class LogMapper:

    @classmethod
    def map_log_entry_to_response(cls, log_entry: LogEntry | None) -> LogResponse | None:
        if log_entry is None:
            return None
        else:
            return LogResponse(
                id=log_entry.id,
                date_time=log_entry.date_time,
                log_level=log_entry.log_level,
                log_type=log_entry.log_type,
                log_message=log_entry.log_message,
                class_name=log_entry.class_name,
                function_name=log_entry.function_name,
                related_object_type=log_entry.related_object_type,
                related_object_id=log_entry.related_object_id,
                details_json=log_entry.details_json,
            )

    @classmethod
    def map_log_entries_to_response(cls, log_entries: list[LogEntry] | None) -> LatestLogsResponse:
        if log_entries is None or len(log_entries) == 0:
            return LatestLogsResponse(items=None)
        else:
            responses: list[LogResponse | None] = []
            for entry in log_entries:
                responses.append(cls.map_log_entry_to_response(entry))

            return LatestLogsResponse(items=responses)
