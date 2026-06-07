from database.base_repository import BaseRepository
from sqlite3 import Cursor
from models import OutageDetectorResult, OutageChangeState
from typing import Any
from exceptions import DBOperationFailedException


class OutageRepository(BaseRepository):

    def _save_internal(self, cursor: Cursor, outage_detection_results: list[OutageDetectorResult]) -> None:
        sql: str = ""
        params: tuple[str, str, str, str | None, str | None, float | None, int | None, int | None] = (
            "",
            "",
            "",
            None,
            None,
            None,
            None,
            None,
        )
        try:
            sql = """
                    INSERT INTO outages (connection_state, last_connection_test, change_state, start_time, end_time, 
                    duration_sec, started_group_id, ended_group_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """

            for result in outage_detection_results:
                params = (
                    result.connection_state,
                    result.last_connection_test,
                    result.change_state,
                    result.start_time,
                    result.end_time,
                    result.duration_sec,
                    result.started_group_id,
                    result.ended_group_id,
                )

                if result.change_state != OutageChangeState.ENDED.value:
                    raise Exception("Can't save OutageDetectorResult. Change_state is not ENDED")

                cursor.execute(sql, params)

                if cursor.lastrowid is None:
                    raise Exception("Could not calculate id.")

                result.set_outage_id(cursor.lastrowid)

                self._log_statement(
                    "OutageRepository",
                    "save",
                    cursor,
                    {"sql": sql, "params": params},
                )
        except Exception as ex:
            raise DBOperationFailedException("OutageRepository", "_save_internal", sql, params, str(ex))

    def _load_internal(self, cursor: Cursor, internal_where_statement: str = "") -> list[OutageDetectorResult]:
        sql: str = ""
        try:
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
        except Exception as ex:
            raise DBOperationFailedException("OutageRepository", "_load_internal", sql, (), str(ex))

    def save(self, outage_detection_results: list[OutageDetectorResult]) -> None:
        return self._database_manager.run_in_transaction(lambda cursor: self._save_internal(cursor, outage_detection_results))

    def load(self, internal_where_statement: str = "") -> list[OutageDetectorResult]:
        return self._database_manager.run_in_transaction(lambda cursor: self._load_internal(cursor, internal_where_statement))
