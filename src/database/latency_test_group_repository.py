from models import LatencyTestGroupResult
from database.base_repository import BaseRepository
from sqlite3 import Cursor
from typing import Any


class LatencyTestGroupRepository(BaseRepository):

    def _save_internal(self, cursor: Cursor, latency_test_group_result: LatencyTestGroupResult) -> int:
        sql = """
                INSERT INTO latency_test_groups (start_time, end_time, time_needed_sec, any_success, group_success) 
                VALUES (?, ?, ?, ?, ?)
        """

        group_params: tuple[str | None, str, float | None, int, int] = (
            latency_test_group_result.start_time,
            latency_test_group_result.end_time,
            latency_test_group_result.time_needed_sec,
            int(latency_test_group_result.any_success),
            int(latency_test_group_result.group_success),
        )

        cursor.execute(sql, group_params)

        if cursor.lastrowid is None:
            raise Exception("Could not calculate group_id")

        group_id: int = cursor.lastrowid

        self._log_statement(
            "LatencyTestGroupRepository",
            "save",
            cursor,
            {"sql": sql, "params": group_params},
        )

        return group_id

    def _load_internal(self, cursor: Cursor, internal_where_statement: str = "") -> list[LatencyTestGroupResult]:
        sql: str = f"""
            SELECT id, start_time, end_time, time_needed_sec, any_success, 
            group_success FROM latency_test_groups {internal_where_statement}
        """

        cursor.execute(sql)
        rows: list[Any] = cursor.fetchall()

        self._log_statement(
            "LatencyTestGroupRepository",
            "load",
            cursor,
            {"sql": sql, "params": {}, "row_count": len(rows)},
        )

        result: list[LatencyTestGroupResult] = []
        for id, start_time, end_time, time_needed_sec, any_success, group_success in rows:
            result.append(LatencyTestGroupResult(id, start_time, end_time, time_needed_sec, any_success, group_success))

        return result

    def save(self, latency_test_group_result: LatencyTestGroupResult) -> int:
        return self._database_manager.run_in_transaction(lambda cursor: self._save_internal(cursor, latency_test_group_result))

    def load(self, internal_where_statement: str = "") -> list[LatencyTestGroupResult]:
        return self._database_manager.run_in_transaction(lambda cursor: self._load_internal(cursor, internal_where_statement))
