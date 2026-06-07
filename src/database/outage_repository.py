from database.base_repository import BaseRepository
from sqlite3 import Cursor
from models import OutageDetectorResult, OutageChangeState
from typing import Any


class OutageRepository(BaseRepository):

    def _save_internal(self, cursor: Cursor, outage_detection_result: OutageDetectorResult) -> int:
        if outage_detection_result.change_state != OutageChangeState.ENDED.value:
            return -1

        sql = """
                INSERT INTO outages (connection_state, last_connection_test, change_state, start_time, end_time, 
                duration_sec, started_group_id, ended_group_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        params: tuple[str, str, str, str | None, str | None, float | None, int | None, int | None] = (
            outage_detection_result.connection_state,
            outage_detection_result.last_connection_test,
            outage_detection_result.change_state,
            outage_detection_result.start_time,
            outage_detection_result.end_time,
            outage_detection_result.duration_sec,
            outage_detection_result.started_group_id,
            outage_detection_result.ended_group_id,
        )

        cursor.execute(sql, params)

        outage_id: int = cursor.lastrowid if cursor.lastrowid is not None else -1

        self._log_statement(
            "OutageRepository",
            "save",
            cursor,
            {"sql": sql, "params": params},
        )

        return outage_id

    def _load_internal(self, cursor: Cursor, internal_where_statement: str = "") -> list[OutageDetectorResult]:
        sql: str = f"""
            SELECT id, connection_state, last_connection_test, change_state, start_time, end_time,  
            duration_sec, started_group_id, ended_group_id FROM outages {internal_where_statement}
        """

        cursor.execute(sql)
        rows: list[Any] = cursor.fetchall()

        self._log_statement(
            "LatencyTestRepository",
            "load",
            cursor,
            {"sql": sql, "params": {}, "row_count": len(rows)},
        )

        result: list[OutageDetectorResult] = []
        for (
            id,
            connection_state,
            last_connection_test,
            change_state,
            start_time,
            end_time,
            duration_sec,
            started_group_id,
            ended_group_id,
        ) in rows:
            result.append(
                OutageDetectorResult(
                    id,
                    connection_state,
                    last_connection_test,
                    change_state,
                    start_time,
                    end_time,
                    duration_sec,
                    started_group_id,
                    ended_group_id,
                )
            )

        return result

    def save(self, outage_detection_result: OutageDetectorResult) -> int:
        return self._database_manager.run_in_transaction(lambda cursor: self._save_internal(cursor, outage_detection_result))

    def load(self, internal_where_statement: str = "") -> list[OutageDetectorResult]:
        return self._database_manager.run_in_transaction(lambda cursor: self._load_internal(cursor, internal_where_statement))
