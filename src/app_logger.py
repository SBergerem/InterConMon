from models import LogEntry, LogLevel, LogType
import logging
from database_manager import DatabaseManager
from datetime import datetime
import json


class AppLogger:
    _logger = logging.getLogger("InterConMon")
    _database_manager = None
    _enabled_console_log_levels = {
        LogLevel.INFO,
        LogLevel.WARNING,
        LogLevel.ERROR,
        LogLevel.CRITICAL,
    }
    _enabled_database_log_levels = {
        LogLevel.INFO,
        LogLevel.WARNING,
        LogLevel.ERROR,
        LogLevel.CRITICAL,
    }

    @classmethod
    def initialize(
        cls,
        enabled_console_log_levels: list[LogLevel],
        enabled_database_log_levels: list[LogLevel],
        database_manager: DatabaseManager,
    ) -> None:
        cls.set_enabled_console_log_levels(enabled_console_log_levels)
        cls.set_enabled_database_log_levels(enabled_database_log_levels)
        cls._database_manager = database_manager

        cls._logger.setLevel(logging.DEBUG)

        if cls._logger.handlers:
            return

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

        console_handler.setFormatter(formatter)
        cls._logger.addHandler(console_handler)

    @classmethod
    def set_enabled_console_log_levels(
        cls,
        enabled_console_log_levels: list[LogLevel],
    ) -> None:
        cls._enabled_console_log_levels = set(enabled_console_log_levels)

    @classmethod
    def set_enabled_database_log_levels(
        cls,
        enabled_database_log_levels: list[LogLevel],
    ) -> None:
        cls._enabled_database_log_levels = set(enabled_database_log_levels)

    @classmethod
    def _is_console_logging_allowed(cls, wanted_log_level: LogLevel) -> bool:
        return wanted_log_level in cls._enabled_console_log_levels

    @classmethod
    def _is_database_logging_allowed(cls, wanted_log_level: LogLevel) -> bool:
        return wanted_log_level in cls._enabled_database_log_levels

    @classmethod
    def _log(
        cls,
        log_level: LogLevel,
        log_type: LogType,
        message: str,
        related_object_type: str | None = None,
        related_object_id: int | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        if cls._is_console_logging_allowed(log_level):
            match log_level:
                case LogLevel.INFO:
                    cls._logger.info(f"[{log_type.value}] {message}")
                case LogLevel.WARNING:
                    cls._logger.warning(f"[{log_type.value}] {message}")
                case LogLevel.ERROR:
                    cls._logger.error(f"[{log_type.value}] {message}")
                case LogLevel.CRITICAL:
                    cls._logger.critical(f"[{log_type.value}] {message}")
                case LogLevel.DEBUG:
                    cls._logger.debug(f"[{log_type.value}] {message}")

        if cls._database_manager is None:
            return

        if cls._is_database_logging_allowed(log_level):
            details_json = None          
            if details is not None:
                details_json = json.dumps(details, ensure_ascii=False)

            try:
                cls._database_manager.save_log_entry(
                    LogEntry(
                        datetime.now().isoformat(),
                        log_level,
                        log_type,
                        message,
                        related_object_type,
                        related_object_id,
                        details_json,
                    )
                )
            except Exception as ex:
                cls._logger.error(f"Could not write log entry to database: {ex}")

    @classmethod
    def debug(
        cls,
        log_type: LogType,
        message: str,
        related_object_type: str | None = None,
        related_object_id: int | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        cls._log(
            LogLevel.DEBUG,
            log_type,
            message,
            related_object_type,
            related_object_id,
            details,
        )

    @classmethod
    def info(
        cls,
        log_type: LogType,
        message: str,
        related_object_type: str | None = None,
        related_object_id: int | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        cls._log(
            LogLevel.INFO,
            log_type,
            message,
            related_object_type,
            related_object_id,
            details,
        )

    @classmethod
    def warning(
        cls,
        log_type: LogType,
        message: str,
        related_object_type: str | None = None,
        related_object_id: int | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        cls._log(
            LogLevel.WARNING,
            log_type,
            message,
            related_object_type,
            related_object_id,
            details,
        )

    @classmethod
    def error(
        cls,
        log_type: LogType,
        message: str,
        related_object_type: str | None = None,
        related_object_id: int | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        cls._log(
            LogLevel.ERROR,
            log_type,
            message,
            related_object_type,
            related_object_id,
            details,
        )

    @classmethod
    def critical(
        cls,
        log_type: LogType,
        message: str,
        related_object_type: str | None = None,
        related_object_id: int | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        cls._log(
            LogLevel.CRITICAL,
            log_type,
            message,
            related_object_type,
            related_object_id,
            details,
        )
