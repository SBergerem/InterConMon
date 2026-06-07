from models import LatencyTestGroupResult
from database.base_repository import BaseRepository
from sqlite3 import Cursor
from typing import Any
from exceptions import DBOperationFailedException


class LatencyTestGroupRepository(BaseRepository):

    def _save_internal(self, cursor: Cursor, latency_test_group_results: list[LatencyTestGroupResult]) -> None:
        sql: str = ""
        params: tuple[str | None, str, float | None, int, int] = ("", "", None, 0, 0)
        try:
            sql = """
                    INSERT INTO latency_test_groups (start_time, end_time, time_needed_sec, any_success, group_success) 
                    VALUES (?, ?, ?, ?, ?)
            """

            for result in latency_test_group_results:
                params: tuple[str | None, str, float | None, int, int] = (
                    result.start_time,
                    result.end_time,
                    result.time_needed_sec,
                    int(result.any_success),
                    int(result.group_success),
                )

                cursor.execute(sql, params)

                if cursor.lastrowid is None:
                    raise Exception("Could not calculate group_id")

                group_id: int = cursor.lastrowid

                self._log_statement(
                    "LatencyTestGroupRepository",
                    "save",
                    cursor,
                    {"sql": sql, "params": params},
                )

                result.set_group_id(group_id)
        except Exception as ex:
            raise DBOperationFailedException("LatencyTestGroupRepository", "_save_internal", sql, params, str(ex))

    def _load_internal(self, cursor: Cursor, internal_where_statement: str = "") -> list[LatencyTestGroupResult]:
        sql: str = ""
        try:
            sql = f"""
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
        except Exception as ex:
            raise DBOperationFailedException("LatencyTestGroupRepository", "_load_internal", sql, (), str(ex))

    def save(self, latency_test_group_results: list[LatencyTestGroupResult]) -> None:
        return self._database_manager.run_in_transaction(lambda cursor: self._save_internal(cursor, latency_test_group_results))

    def load(self, internal_where_statement: str = "") -> list[LatencyTestGroupResult]:
        return self._database_manager.run_in_transaction(lambda cursor: self._load_internal(cursor, internal_where_statement))
