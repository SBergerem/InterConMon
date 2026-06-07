from database.base_repository import BaseRepository
from sqlite3 import Cursor
from typing import Any
from models import LatencyTestResult


class LatencyTestRepository(BaseRepository):

    def _save_internal(self, cursor: Cursor, group_id: int, latency_test: LatencyTestResult) -> None:
        sql = """
                INSERT INTO latency_tests (group_id, date_time, target, success, latency_ms, error_message)  
                VALUES (?, ?, ?, ?, ?, ?)                 
            """

        params: tuple[int, str, str, int, float | None, str | None] = (
            group_id,
            latency_test.date_time,
            latency_test.target,
            int(latency_test.success),
            latency_test.latency_ms,
            latency_test.error_message,
        )

        cursor.execute(sql, params)
        self._log_statement(
            "LatencyTestRepository",
            "save",
            cursor,
            {"sql": sql, "params": params},
        )

    def _load_internal(self, cursor: Cursor, internal_where_statement: str = "") -> list[LatencyTestResult]:
        sql: str = f"""
            SELECT id, group_id, date_time, target, success, latency_ms, error_message FROM latency_tests {internal_where_statement}
        """

        cursor.execute(sql)
        rows: list[Any] = cursor.fetchall()

        self._log_statement(
            "LatencyTestRepository",
            "load",
            cursor,
            {"sql": sql, "params": {}, "row_count": len(rows)},
        )

        result: list[LatencyTestResult] = []
        for id, group_id, date_time, target, success, latency_ms, error_message in rows:
            result.append(LatencyTestResult(id, group_id, date_time, target, success, latency_ms, error_message))

        return result

    def save(self, group_id: int, latency_test: LatencyTestResult) -> None:
        self._database_manager.run_in_transaction(lambda cursor: self._save_internal(cursor, group_id, latency_test))

    def load(self, internal_where_statement: str = "") -> list[LatencyTestResult]:
        return self._database_manager.run_in_transaction(lambda cursor: self._load_internal(cursor, internal_where_statement))
