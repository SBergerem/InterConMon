from database.log_entry_repository import LogEntryRepository
from api.schemas.log_schema import LatestLogsResponse
from api.mappers.log_mapper import LogMapper
from models.models import LogEntry, LogType, LogLevel


class LogService:

    def __init__(self, repository: LogEntryRepository) -> None:
        self._repository: LogEntryRepository = repository

    def get_latest_logs(self, limit: int, log_types: list[LogType] | None, log_levels: list[LogLevel] | None) -> LatestLogsResponse:
        if log_types is None:
            log_types = [LogType.SYSTEM]

        if log_levels is None:
            log_levels = [LogLevel.INFO]

        log_entries: list[LogEntry] = self._repository.load_latest_list(limit, log_types, log_levels)

        return LogMapper.map_log_entries_to_response(log_entries)
