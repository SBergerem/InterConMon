from backend.src.database.base_repository import BaseRepository
from sqlite3 import Cursor
from backend.src.models.models import LogEntry, LogType, LogLevel
from typing import Any
from backend.src.exceptions.exceptions import DBOperationFailedException


class LogEntryRepository(BaseRepository):

    # Can't log here, because it would result in log looping
    def _save_internal(self, cursor: Cursor, log_entries: list[LogEntry]) -> None:
        sql: str = ""
        params: list[tuple[str, str, str, str, str, str, str | None, int | None, str | None]] = []
        try:
            sql = """
                INSERT INTO logs (date_time, log_level, log_type, log_message, class_name, function_name, related_object_type, related_object_id, details_json)        
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            for entry in log_entries:
                params.append(
                    (
                        entry.date_time,
                        entry.log_level,
                        entry.log_type,
                        entry.log_message,
                        entry.class_name,
                        entry.function_name,
                        entry.related_object_type,
                        entry.related_object_id,
                        entry.details_json,
                    )
                )

            cursor.executemany(sql, params)
        except Exception as ex:
            raise DBOperationFailedException("LogEntryRepository", "_save_internal", sql, params, str(ex))

    def _load_internal(
        self, cursor: Cursor, statement_addition: str = "", addition_placeholder_values: list[Any] | None = None
    ) -> list[LogEntry]:
        sql: str = ""
        try:
            sql: str = f"""
                SELECT id, date_time, log_level, log_type, log_message, class_name, function_name, 
                related_object_type, related_object_id, details_json FROM logs {statement_addition}
            """

            cursor.execute(sql, addition_placeholder_values if addition_placeholder_values is not None else [])
            rows: list[Any] = cursor.fetchall()

            log_entries: list[LogEntry] = []
            for (
                id,
                date_time,
                log_level,
                log_type,
                log_message,
                class_name,
                function_name,
                related_object_type,
                related_object_id,
                details_json,
            ) in rows:
                log_entries.append(
                    LogEntry(
                        id,
                        date_time,
                        log_level,
                        log_type,
                        log_message,
                        class_name,
                        function_name,
                        related_object_type,
                        related_object_id,
                        details_json,
                    )
                )

            return log_entries
        except Exception as ex:
            raise DBOperationFailedException(
                "LogEntryRepository", "_load_internal", sql, {"addition_placeholder_values": addition_placeholder_values}, str(ex)
            )

    def save(self, log_entries: list[LogEntry], outer_cursor: Cursor | None = None) -> None:
        self._database_manager.run_in_transaction(lambda cursor: self._save_internal(cursor, log_entries), outer_cursor)

    def load(self, statement_addition: str = "") -> list[LogEntry]:
        return self._database_manager.run_in_transaction(lambda cursor: self._load_internal(cursor, statement_addition))

    def load_latest_list(self, limit: int, log_types: list[LogType], log_levels: list[LogLevel]) -> list[LogEntry]:

        statement_addition: str = f" ORDER BY date_time DESC LIMIT ?"
        where_parts: list[str] = []
        params: list[Any] = []

        if len(log_types) > 0:
            params.extend([log_type.value for log_type in log_types])
            log_type_placeholders: str = ",".join("?" for _ in log_types)
            where_parts.append(f"log_type IN ({log_type_placeholders})")

        if len(log_levels) > 0:
            params.extend([log_level.value for log_level in log_levels])
            log_level_placeholders: str = ",".join("?" for _ in log_levels)
            where_parts.append(f"log_level IN ({log_level_placeholders})")

        if len(where_parts) > 0:
            joined_where_parts: str = " AND ".join(where_parts)
            where_addition: str = f" WHERE {joined_where_parts}"
        else:
            where_addition = ""

        statement_addition = where_addition + statement_addition

        params.append(limit)

        result: list[LogEntry] = self._database_manager.run_in_transaction(
            lambda cursor: self._load_internal(cursor, statement_addition, params)
        )
        return result
