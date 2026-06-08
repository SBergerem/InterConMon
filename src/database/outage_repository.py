from database.base_repository import BaseRepository
from sqlite3 import Cursor
from models import OutageDetection, OutageChangeState
from typing import Any
from exceptions import DBOperationFailedException


class OutageRepository(BaseRepository):

    def _save_internal(self, cursor: Cursor, outage_detections: list[OutageDetection]) -> None:
        sql: str = ""
        params: tuple[str, str, str, str, str | None, str | None, float | None, int | None, int | None] = (
            "",
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
                    INSERT INTO outages (connection_state, last_connection_test, change_state, test_target_type, start_time, end_time, 
                    duration_sec, started_group_id, ended_group_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            for detections in outage_detections:
                params = (
                    detections.connection_state,
                    detections.last_connection_test,
                    detections.change_state,
                    detections.test_target_type,
                    detections.start_time,
                    detections.end_time,
                    detections.duration_sec,
                    detections.started_group_id,
                    detections.ended_group_id,
                )

                if detections.change_state != OutageChangeState.ENDED.value:
                    raise Exception("Can't save OutageDetection. Change_state is not ENDED")

                cursor.execute(sql, params)

                if cursor.lastrowid is None:
                    raise Exception("Could not calculate id.")

                detections.set_outage_id(cursor.lastrowid)

                self._log_statement(
                    "OutageRepository",
                    "_save_internal",
                    cursor,
                    {"sql": sql, "params": params},
                )
        except Exception as ex:
            raise DBOperationFailedException("OutageRepository", "_save_internal", sql, params, str(ex))

    def _load_internal(self, cursor: Cursor, internal_where_statement: str = "") -> list[OutageDetection]:
        sql: str = ""
        try:
            sql: str = f"""
                SELECT id, connection_state, last_connection_test, change_state, test_target_type, start_time, end_time,  
                duration_sec, started_group_id, ended_group_id FROM outages {internal_where_statement}
            """

            cursor.execute(sql)
            rows: list[Any] = cursor.fetchall()

            self._log_statement(
                "LatencyTestRepository",
                "_load_internal",
                cursor,
                {"sql": sql, "params": {}, "row_count": len(rows)},
            )

            detection: list[OutageDetection] = []
            for (
                id,
                connection_state,
                last_connection_test,
                change_state,
                test_target_type,
                start_time,
                end_time,
                duration_sec,
                started_group_id,
                ended_group_id,
            ) in rows:
                detection.append(
                    OutageDetection(
                        id,
                        connection_state,
                        last_connection_test,
                        change_state,
                        test_target_type,
                        start_time,
                        end_time,
                        duration_sec,
                        started_group_id,
                        ended_group_id,
                    )
                )

            return detection
        except Exception as ex:
            raise DBOperationFailedException("OutageRepository", "_load_internal", sql, (), str(ex))

    def save(self, outage_detections: list[OutageDetection]) -> None:
        return self._database_manager.run_in_transaction(lambda cursor: self._save_internal(cursor, outage_detections))

    def load(self, internal_where_statement: str = "") -> list[OutageDetection]:
        return self._database_manager.run_in_transaction(lambda cursor: self._load_internal(cursor, internal_where_statement))
