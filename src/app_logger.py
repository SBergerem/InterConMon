from models import LogEntry, LogLevel, LogType


class AppLogger:
    _current_log_level = LogLevel.INFO

    @classmethod
    def set_log_level(cls, log_level: LogLevel):
        cls._current_log_level = log_level

    @classmethod
    def debug(
        cls,
        log_type: LogType,
        message: str,
        related_object_type: str | None = None,
        related_object_id: int | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        pass

    @classmethod
    def info(
        cls,
        log_type: LogType,
        message: str,
        related_object_type: str | None = None,
        related_object_id: int | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        pass

    @classmethod
    def warning(
        cls,
        log_type: LogType,
        message: str,
        related_object_type: str | None = None,
        related_object_id: int | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        pass

    @classmethod
    def error(
        cls,
        log_type: LogType,
        message: str,
        related_object_type: str | None = None,
        related_object_id: int | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        pass

    @classmethod
    def critical(
        cls,
        log_type: LogType,
        message: str,
        related_object_type: str | None = None,
        related_object_id: int | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        pass
