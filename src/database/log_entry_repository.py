from database.base_repository import BaseRepository
from sqlite3 import Cursor
from models import LogEntry
from typing import Any


class LogEntryRepository(BaseRepository):

    # Can't log here, because it would result in log looping
    def _save_internal(self, cursor: Cursor, log_entry: LogEntry) -> None:
        sql = """
            INSERT INTO logs (date_time, log_level, log_type, log_message, class_name, function_name, related_object_type, related_object_id, details_json)        
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params: tuple[str, str, str, str, str, str, str | None, int | None, str | None] = (
            log_entry.date_time,
            log_entry.log_level,
            log_entry.log_type,
            log_entry.log_message,
            log_entry.class_name,
            log_entry.function_name,
            log_entry.related_object_type,
            log_entry.related_object_id,
            log_entry.details_json,
        )

        cursor.execute(sql, params)

    def _load_internal(self, cursor: Cursor, internal_where_statement: str = "") -> list[LogEntry]:
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

    def save(self, log_entry: LogEntry, outer_cursor: Cursor | None = None) -> None:
        self._database_manager.run_in_transaction(lambda cursor: self._save_internal(cursor, log_entry), outer_cursor)

    def load(self, internal_where_statement: str = "") -> list[LogEntry]:
        return self._database_manager.run_in_transaction(lambda cursor: self._load_internal(cursor, internal_where_statement))
