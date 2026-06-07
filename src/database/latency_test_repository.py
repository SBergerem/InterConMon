from database.base_repository import BaseRepository
from sqlite3 import Cursor
from typing import Any
from models import LatencyTestResult
from exceptions import DBOperationFailedException


class LatencyTestRepository(BaseRepository):

    def _save_internal(self, cursor: Cursor, latency_tests: list[LatencyTestResult]) -> None:
        try:
            sql = """
                    INSERT INTO latency_tests (group_id, date_time, target, success, latency_ms, error_message)  
                    VALUES (?, ?, ?, ?, ?, ?)                 
                """

            params: list[tuple[int, str, str, int, float | None, str | None]] = []
            for test in latency_tests:
                params.append((test.group_id, test.date_time, test.target, int(test.success), test.latency_ms, test.error_message))

            cursor.executemany(sql, params)
            self._log_statement(
                "LatencyTestRepository",
                "save",
                cursor,
                {"sql": sql, "params": params},
            )
        except Exception as ex:
            raise DBOperationFailedException(str(ex), "LatencyTestRepository", "_save_internal")

    def _load_internal(self, cursor: Cursor, internal_where_statement: str = "") -> list[LatencyTestResult]:
        try:
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
        except Exception as ex:
            raise DBOperationFailedException(str(ex), "LatencyTestRepository", "_load_internal")

    def save(self, latency_tests: list[LatencyTestResult]) -> None:
        self._database_manager.run_in_transaction(lambda cursor: self._save_internal(cursor, latency_tests))

    def load(self, internal_where_statement: str = "") -> list[LatencyTestResult]:
        return self._database_manager.run_in_transaction(lambda cursor: self._load_internal(cursor, internal_where_statement))
