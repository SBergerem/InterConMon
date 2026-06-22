from models.models import LatencyTestGroup
from database.base_repository import BaseRepository
from sqlite3 import Cursor
from typing import Any
from exceptions.exceptions import DBOperationFailedException


class LatencyTestGroupRepository(BaseRepository):

    def _save_internal(self, cursor: Cursor, latency_test_groups: list[LatencyTestGroup]) -> None:
        sql: str = ""
        params: tuple[str | None, str, float | None, int, int, str] = ("", "", None, 0, 0, "")
        try:
            sql = """
                INSERT INTO latency_test_groups (start_time, end_time, time_needed_sec, any_success, group_success, test_target_type) 
                VALUES (?, ?, ?, ?, ?, ?)
            """

            for group in latency_test_groups:
                params = (
                    group.start_time,
                    group.end_time,
                    group.time_needed_sec,
                    int(group.any_success),
                    int(group.group_success),
                    group.test_target_type.value,
                )

                cursor.execute(sql, params)

                if cursor.lastrowid is None:
                    raise Exception("Could not calculate group_id")

                group_id: int = cursor.lastrowid

                self._log_statement(
                    "LatencyTestGroupRepository",
                    "_save_internal",
                    cursor,
                    {"sql": sql, "params": params},
                )

                group.set_id(group_id)
        except Exception as ex:
            raise DBOperationFailedException("LatencyTestGroupRepository", "_save_internal", sql, params, str(ex))

    def _load_internal(
        self, cursor: Cursor, statement_addition: str = "", addition_placeholder_values: list[Any] = []
    ) -> list[LatencyTestGroup]:
        sql: str = ""
        try:
            sql = f"""
                SELECT id, start_time, end_time, time_needed_sec, any_success,
                group_success, test_target_type FROM latency_test_groups {statement_addition}
            """

            cursor.execute(sql, addition_placeholder_values)
            rows: list[Any] = cursor.fetchall()

            self._log_statement(
                "LatencyTestGroupRepository",
                "_load_internal",
                cursor,
                {"sql": sql, "params": {}, "row_count": len(rows)},
            )

            groups: list[LatencyTestGroup] = []
            for id, start_time, end_time, time_needed_sec, any_success, group_success, test_target_type in rows:
                groups.append(LatencyTestGroup(id, start_time, end_time, time_needed_sec, any_success, group_success, test_target_type))

            return groups
        except Exception as ex:
            raise DBOperationFailedException("LatencyTestGroupRepository", "_load_internal", sql, (), str(ex))

    def save(self, latency_test_groups: list[LatencyTestGroup]) -> None:
        return self._database_manager.run_in_transaction(lambda cursor: self._save_internal(cursor, latency_test_groups))

    def save_in_transaction(self, latency_test_groups: list[LatencyTestGroup], cursor: Cursor) -> None:
        self._save_internal(cursor, latency_test_groups)

    def load(self, statement_addition: str = "") -> list[LatencyTestGroup]:
        return self._database_manager.run_in_transaction(lambda cursor: self._load_internal(cursor, statement_addition))
