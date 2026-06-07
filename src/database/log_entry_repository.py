from database.base_repository import BaseRepository
from sqlite3 import Cursor
from models import LogEntry
from typing import Any
from exceptions import DBOperationFailedException


class LogEntryRepository(BaseRepository):

    # Can't log here, because it would result in log looping
    def _save_internal(self, cursor: Cursor, log_entries: list[LogEntry]) -> None:
        try:
            sql = """
                INSERT INTO logs (date_time, log_level, log_type, log_message, class_name, function_name, related_object_type, related_object_id, details_json)        
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            params: list[tuple[str, str, str, str, str, str, str | None, int | None, str | None]] = []
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
            raise DBOperationFailedException(str(ex), "LogEntryRepository", "_save_internal")

    def _load_internal(self, cursor: Cursor, internal_where_statement: str = "") -> list[LogEntry]:
        try:
            sql: str = f"""
                SELECT id, date_time, log_level, log_type, log_message, class_name, function_name, 
                related_object_type, related_object_id, details_json FROM logs {internal_where_statement}
            """

            cursor.execute(sql)
            rows: list[Any] = cursor.fetchall()

            result: list[LogEntry] = []
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
                result.append(
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

            return result
        except Exception as ex:
            raise DBOperationFailedException(str(ex), "LogEntryRepository", "_load_internal")

    def save(self, log_entries: list[LogEntry], outer_cursor: Cursor | None = None) -> None:
        self._database_manager.run_in_transaction(lambda cursor: self._save_internal(cursor, log_entries), outer_cursor)

    def load(self, internal_where_statement: str = "") -> list[LogEntry]:
        return self._database_manager.run_in_transaction(lambda cursor: self._load_internal(cursor, internal_where_statement))
