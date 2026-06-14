from database.base_repository import BaseRepository
from sqlite3 import Cursor
from models import Outage, OutageChangeState
from typing import Any
from exceptions import DBOperationFailedException


class OutageRepository(BaseRepository):

    def _save_internal(self, cursor: Cursor, outages: list[Outage]) -> None:
        sql: str = ""
        params: tuple[str, str, str, str, str, str | None, str | None, float | None, int | None, int | None] = (
            "",
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
                INSERT INTO outages (date_time, reachability_state, last_connection_test, change_state, test_target_type, start_time, end_time, 
                duration_sec, started_group_id, ended_group_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            for outage in outages:
                params = (
                    outage.date_time,
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

    def _update_internal(self, cursor: Cursor, outages: list[Outage]) -> None:
        sql: str = ""
        params: tuple[str, str, str, str, str, str | None, str | None, float | None, int | None, int | None, int] = (
            "",
            "",
            "",
            "",
            "",
            None,
            None,
            None,
            None,
            None,
            0,
        )
        try:
            for outage in outages:
                params = (
                    outage.date_time,
                    outage.reachability_state.value,
                    outage.last_connection_test,
                    outage.change_state.value,
                    outage.test_target_type.value,
                    outage.start_time,
                    outage.end_time,
                    outage.duration_sec,
                    outage.started_group_id,
                    outage.ended_group_id,
                    outage.id,
                )

            sql = f"""
                UPDATE outages SET date_time = ?, reachability_state = ?, last_connection_test = ?, change_state = ?, test_target_type = ?, start_time = ?, end_time = ?, 
                duration_sec = ?, started_group_id = ?, ended_group_id = ? WHERE id = ?
            """

            cursor.execute(sql, params)

            self._log_statement(
                "OutageRepository",
                "_update_internal",
                cursor,
                {"sql": sql, "params": params},
            )
        except Exception as ex:
            raise DBOperationFailedException("OutageRepository", "_update_internal", sql, params, str(ex))

    def _load_internal(self, cursor: Cursor, statement_addition: str = "", addition_placeholder_values: list[Any] = []) -> list[Outage]:
        sql: str = ""
        try:
            sql: str = f"""
                SELECT id, date_time, reachability_state, last_connection_test, change_state, test_target_type, start_time, end_time,  
                duration_sec, started_group_id, ended_group_id FROM outages {statement_addition}
            """

            cursor.execute(sql, addition_placeholder_values)
            rows: list[Any] = cursor.fetchall()

            self._log_statement(
                "OutageRepository",
                "_load_internal",
                cursor,
                {"sql": sql, "params": {}, "row_count": len(rows)},
            )

            outages: list[Outage] = []

            for (
                id,
                date_time,
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
                        date_time,
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

    def load(self, statement_addition: str = "") -> list[Outage]:
        return self._database_manager.run_in_transaction(lambda cursor: self._load_internal(cursor, statement_addition))

    def update(self, outages: list[Outage]) -> None:
        return self._database_manager.run_in_transaction(lambda cursor: self._update_internal(cursor, outages))

    def load_latest(self) -> Outage | None:
        result: list[Outage] = self._database_manager.run_in_transaction(
            lambda cursor: self._load_internal(cursor, "ORDER BY date_time DESC LIMIT 1")
        )
        return result[0] if len(result) == 1 else None
