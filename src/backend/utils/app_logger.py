from backend.models.models import LogEntry, LogLevel, LogType
import logging
from logging import Logger, StreamHandler
from datetime import datetime
import json
from typing import TYPE_CHECKING, TextIO
from sqlite3 import Cursor
from backend.database.log_entry_repository import LogEntryRepository

if TYPE_CHECKING:
    from backend.database.database_manager import DatabaseManager


class AppLogger:
    _logger: Logger = logging.getLogger("InterConMon")
    _log_entry_repository: LogEntryRepository
    _enabled_console_log_levels: set[LogLevel] = {LogLevel.INFO}
    _enabled_database_log_levels: set[LogLevel] = {LogLevel.INFO}
    _is_initialized: bool = False

    @classmethod
    def _colorize_console_message(cls, log_level: LogLevel, message: str) -> str:
        reset = "\033[0m"

        colors: dict[LogLevel, str] = {
            LogLevel.INFO: "\033[32m",
            LogLevel.WARNING: "\033[33m",
            LogLevel.ERROR: "\033[31m",
            LogLevel.CRITICAL: "\033[91m",
            LogLevel.DEBUG: "\033[34m",
            LogLevel.EXTENDED_DEBUG: "\033[36m",
            LogLevel.DETAILED_DEBUG: "\033[38;5;110m",
        }

        color = colors.get(log_level, "")
        return f"{color}{message}{reset}"

    @classmethod
    def pre_initialize(cls) -> None:
        cls._logger.setLevel(logging.DEBUG)

        if cls._logger.handlers:
            return

        console_handler: StreamHandler[TextIO] = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s:  %(levelname)-8s %(message)s")

        console_handler.setFormatter(formatter)
        cls._logger.addHandler(console_handler)

    @classmethod
    def initialize(
        cls,
        enabled_console_log_levels: list[LogLevel],
        enabled_database_log_levels: list[LogLevel],
        database_manager: DatabaseManager,
    ) -> None:
        cls.set_enabled_console_log_levels(enabled_console_log_levels)
        cls.set_enabled_database_log_levels(enabled_database_log_levels)
        cls._log_entry_repository = LogEntryRepository(database_manager)
        cls._is_initialized = True

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
        class_name: str,
        function_name: str,
        related_object_type: str | None = None,
        related_object_id: int | None = None,
        details: dict[str, object] | None = None,
        outer_cursor: Cursor | None = None,
        skip_database: bool = False,
    ) -> None:
        if cls._is_console_logging_allowed(log_level):
            formatted_message: str = (
                f"{"":<11} | "
                f"{"[" + log_type.value.upper() + "]":<10} | "
                f"{class_name:<40} | "
                f"{function_name:<30}"
                f"\n--->   {message}"
            )

            json_text: str = ""
            if details is not None:
                json_text = json.dumps(details, ensure_ascii=False)
                json_text = " ".join(json_text.split())
                json_text = json_text.replace("\\n", "")
                formatted_message = f"{formatted_message} | " f"{json_text}"

            formatted_message = formatted_message + "\n\n"

            match log_level:
                case LogLevel.INFO:
                    formatted_message: str = (
                        f"{"":<11} | " f"{"[" + log_type.value.upper() + "]":<10} | " f"{"-":<40} | " f"{"-":<30}" f"\n--->   {message}\n\n"
                    )

                    cls._logger.info(cls._colorize_console_message(LogLevel.INFO, formatted_message))
                case LogLevel.WARNING:
                    cls._logger.warning(cls._colorize_console_message(LogLevel.WARNING, formatted_message))
                case LogLevel.ERROR:
                    cls._logger.error(cls._colorize_console_message(LogLevel.ERROR, formatted_message))
                case LogLevel.CRITICAL:
                    cls._logger.critical(cls._colorize_console_message(LogLevel.CRITICAL, formatted_message))
                case LogLevel.DEBUG:
                    cls._logger.debug(cls._colorize_console_message(LogLevel.DEBUG, formatted_message))
                case LogLevel.EXTENDED_DEBUG:
                    formatted_message: str = (
                        f"{"(EXTENDED) ":<11} | "
                        f"{"[" + log_type.value.upper() + "]":<10} | "
                        f"{class_name:<40} | "
                        f"{function_name:<30}"
                        f"\n--->   {message}\n\n"
                    )

                    cls._logger.debug(cls._colorize_console_message(LogLevel.EXTENDED_DEBUG, formatted_message))
                case LogLevel.DETAILED_DEBUG:
                    formatted_message: str = (
                        f"{"(DETAILED) ":<11} | "
                        f"{"[" + log_type.value.upper() + "]":<10} | "
                        f"{class_name:<40} | "
                        f"{function_name:<30}"
                        f"\n--->   {message}"
                    )

                    if details is not None:
                        formatted_message = f"{formatted_message} | " f"{json_text}"

                    formatted_message = formatted_message + "\n\n"

                    cls._logger.debug(cls._colorize_console_message(LogLevel.DETAILED_DEBUG, formatted_message))

        if skip_database or not cls._is_initialized:
            return

        if cls._is_database_logging_allowed(log_level):
            details_json: str | None = None
            if details is not None:
                details_json = json.dumps(details, ensure_ascii=False)
                details_json = " ".join(details_json.split())
                details_json = details_json.replace("\\n", "")
            try:
                cls._log_entry_repository.save(
                    [
                        LogEntry(
                            0,
                            datetime.now().isoformat(),
                            log_level.value,
                            log_type.value,
                            message,
                            class_name,
                            function_name,
                            related_object_type,
                            related_object_id,
                            details_json,
                        )
                    ],
                    outer_cursor=outer_cursor,
                )
            except Exception as ex:
                formatted_message: str = (
                    f"{"":<11} | "
                    f"{"[" + log_type.value.upper() + "]":<10} | "
                    f"{class_name:<30} | "
                    f"{function_name:<30} | "
                    f"Could not write log entry (message: {message}) to database: {ex}"
                )

                cls._logger.error(formatted_message)

    @classmethod
    def debug(
        cls,
        log_type: LogType,
        message: str,
        class_name: str,
        function_name: str,
        related_object_type: str | None = None,
        related_object_id: int | None = None,
        details: dict[str, object] | None = None,
        outer_cursor: Cursor | None = None,
        skip_database: bool = False,
    ) -> None:
        cls._log(
            LogLevel.DEBUG,
            log_type,
            message,
            class_name,
            function_name,
            related_object_type,
            related_object_id,
            details,
            outer_cursor,
            skip_database,
        )

    @classmethod
    def extended_debug(
        cls,
        log_type: LogType,
        message: str,
        class_name: str,
        function_name: str,
        related_object_type: str | None = None,
        related_object_id: int | None = None,
        details: dict[str, object] | None = None,
        outer_cursor: Cursor | None = None,
        skip_database: bool = False,
    ) -> None:
        cls._log(
            LogLevel.EXTENDED_DEBUG,
            log_type,
            message,
            class_name,
            function_name,
            related_object_type,
            related_object_id,
            details,
            outer_cursor,
            skip_database,
        )

    @classmethod
    def detailed_debug(
        cls,
        log_type: LogType,
        message: str,
        class_name: str,
        function_name: str,
        related_object_type: str | None = None,
        related_object_id: int | None = None,
        details: dict[str, object] | None = None,
        outer_cursor: Cursor | None = None,
        skip_database: bool = False,
    ) -> None:
        cls._log(
            LogLevel.DETAILED_DEBUG,
            log_type,
            message,
            class_name,
            function_name,
            related_object_type,
            related_object_id,
            details,
            outer_cursor,
            skip_database,
        )

    @classmethod
    def info(
        cls,
        log_type: LogType,
        message: str,
        class_name: str,
        function_name: str,
        related_object_type: str | None = None,
        related_object_id: int | None = None,
        details: dict[str, object] | None = None,
        outer_cursor: Cursor | None = None,
        skip_database: bool = False,
    ) -> None:
        cls._log(
            LogLevel.INFO,
            log_type,
            message,
            class_name,
            function_name,
            related_object_type,
            related_object_id,
            details,
            outer_cursor,
            skip_database,
        )

    @classmethod
    def warning(
        cls,
        log_type: LogType,
        message: str,
        class_name: str,
        function_name: str,
        related_object_type: str | None = None,
        related_object_id: int | None = None,
        details: dict[str, object] | None = None,
        outer_cursor: Cursor | None = None,
        skip_database: bool = False,
    ) -> None:
        cls._log(
            LogLevel.WARNING,
            log_type,
            message,
            class_name,
            function_name,
            related_object_type,
            related_object_id,
            details,
            outer_cursor,
            skip_database,
        )

    @classmethod
    def error(
        cls,
        log_type: LogType,
        message: str,
        class_name: str,
        function_name: str,
        related_object_type: str | None = None,
        related_object_id: int | None = None,
        details: dict[str, object] | None = None,
        outer_cursor: Cursor | None = None,
        skip_database: bool = False,
    ) -> None:
        cls._log(
            LogLevel.ERROR,
            log_type,
            message,
            class_name,
            function_name,
            related_object_type,
            related_object_id,
            details,
            outer_cursor,
            skip_database,
        )

    @classmethod
    def critical(
        cls,
        log_type: LogType,
        message: str,
        class_name: str,
        function_name: str,
        related_object_type: str | None = None,
        related_object_id: int | None = None,
        details: dict[str, object] | None = None,
        outer_cursor: Cursor | None = None,
        skip_database: bool = False,
    ) -> None:
        cls._log(
            LogLevel.CRITICAL,
            log_type,
            message,
            class_name,
            function_name,
            related_object_type,
            related_object_id,
            details,
            outer_cursor,
            skip_database,
        )
