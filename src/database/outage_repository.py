from database.base_repository import BaseRepository
from sqlite3 import Cursor
from models import Outage, OutageChangeState
from typing import Any
from exceptions import DBOperationFailedException


class OutageRepository(BaseRepository):

    def _save_internal(self, cursor: Cursor, outages: list[Outage]) -> None:
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
                INSERT INTO outages (reachability_state, last_connection_test, change_state, test_target_type, start_time, end_time, 
                duration_sec, started_group_id, ended_group_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            for outage in outages:
                params = (
                    outage.reachability_state.value,
                    outage.last_connection_test,
                    outage.change_state.value,
                    outage.test_target_type.value,
                    outage.start_time,
                    outage.end_time,
                    outage.duration_sec,
                    outage.started_group_id,
                    outage.ended_group_id,
                )

                if outage.change_state != OutageChangeState.ENDED:
                    raise Exception("Can't save Outage. Change_state is not ENDED")

                cursor.execute(sql, params)

                if cursor.lastrowid is None:
                    raise Exception("Could not calculate id.")

                outage.set_id(cursor.lastrowid)

                self._log_statement(
                    "OutageRepository",
                    "_save_internal",
                    cursor,
                    {"sql": sql, "params": params},
                )
        except Exception as ex:
            raise DBOperationFailedException("OutageRepository", "_save_internal", sql, params, str(ex))

    def _load_internal(self, cursor: Cursor, internal_where_statement: str = "") -> list[Outage]:
        sql: str = ""
        try:
            sql: str = f"""
                SELECT id, reachability_state, last_connection_test, change_state, test_target_type, start_time, end_time,  
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

            outages: list[Outage] = []
            for (
                id,
                reachability_state,
                last_connection_test,
                change_state,
                test_target_type,
                start_time,
                end_time,
                duration_sec,
                started_group_id,
                ended_group_id,
            ) in rows:
                outages.append(
                    Outage(
                        id,
                        reachability_state,
                        last_connection_test,
                        change_state,
                        test_target_type,
                        start_time,
                        end_time,
                        duration_sec,
                        started_group_id,
                        None,
                        ended_group_id,
                        None,
                    )
                )

            return outages
        except Exception as ex:
            raise DBOperationFailedException("OutageRepository", "_load_internal", sql, (), str(ex))

    def save(self, outages: list[Outage]) -> None:
        return self._database_manager.run_in_transaction(lambda cursor: self._save_internal(cursor, outages))

    def load(self, internal_where_statement: str = "") -> list[Outage]:
        return self._database_manager.run_in_transaction(lambda cursor: self._load_internal(cursor, internal_where_statement))
