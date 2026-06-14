from database.base_repository import BaseRepository
from sqlite3 import Cursor
from typing import Any
from models import LatencyTest, LatencyTestGroup
from exceptions import DBOperationFailedException


class LatencyTestRepository(BaseRepository):

    def _save_internal(self, cursor: Cursor, latency_tests: list[LatencyTest]) -> None:
        sql: str = ""
        params: tuple[int, str, str, str, int, float | None, str | None] = (0, "", "", "", 0, None, None)
        try:
            sql = """
                    INSERT INTO latency_tests (group_id, date_time, target, test_target_type, success, latency_ms, error_message)  
                    VALUES (?, ?, ?, ?, ?, ?, ?)                 
                """

            for test in latency_tests:
                params = (
                    test.group_id,
                    test.date_time,
                    test.target,
                    test.test_target_type.value,
                    int(test.success),
                    test.latency_ms,
                    test.error_message,
                )

                cursor.execute(sql, params)

                if cursor.lastrowid is None:
                    raise Exception("Could not calculate latency_test_id")

                test.set_id(cursor.lastrowid)

                self._log_statement(
                    "LatencyTestRepository",
                    "_save_internal",
                    cursor,
                    {"sql": sql, "params": params},
                )
        except Exception as ex:
            raise DBOperationFailedException("LatencyTestRepository", "_save_internal", sql, params, str(ex))

    def _load_internal(
        self, cursor: Cursor, statement_addition: str = "", addition_placeholder_values: list[Any] = []
    ) -> list[LatencyTest]:
        sql: str = ""
        try:
            sql: str = f"""
                SELECT id, group_id, date_time, target, test_target_type, success, latency_ms, error_message FROM latency_tests {statement_addition}
            """

            cursor.execute(sql, addition_placeholder_values)
            rows: list[Any] = cursor.fetchall()

            self._log_statement(
                "LatencyTestRepository",
                "_load_internal",
                cursor,
                {"sql": sql, "params": {}, "row_count": len(rows)},
            )

            test: list[LatencyTest] = []
            for id, group_id, date_time, target, test_target_type, success, latency_ms, error_message in rows:
                test.append(LatencyTest(id, group_id, date_time, target, test_target_type, success, latency_ms, error_message))

            return test
        except Exception as ex:
            raise DBOperationFailedException("LatencyTestRepository", "_load_internal", sql, (), str(ex))

    def save(self, latency_tests: list[LatencyTest]) -> None:
        self._database_manager.run_in_transaction(lambda cursor: self._save_internal(cursor, latency_tests))

    def save_in_transaction(self, latency_tests: list[LatencyTest], cursor: Cursor) -> None:
        self._save_internal(cursor, latency_tests)

    def load(self, statement_addition: str = "") -> list[LatencyTest]:
        return self._database_manager.run_in_transaction(lambda cursor: self._load_internal(cursor, statement_addition))

    def load_in_test_group(self, latency_test_group: LatencyTestGroup) -> None:
        latency_tests: list[LatencyTest] = self._database_manager.run_in_transaction(
            lambda cursor: self._load_internal(cursor, "WHERE group_id = ?", [latency_test_group.id])
        )

        latency_test_group.tests = latency_tests
