from database.base_repository import BaseRepository
from sqlite3 import Cursor
from typing import Any
from models import ConnectionDiagnosis
from exceptions import DBOperationFailedException


class ConnectionDiagnosisRepository(BaseRepository):

    def _save_internal(self, cursor: Cursor, diagnoses: list[ConnectionDiagnosis]) -> None:
        sql: str = ""
        params: tuple[str, str, int, int | None] = ("", "", 0, 0)
        try:
            sql = """
                    INSERT INTO connection_diagnoses (date_time, network_diagnosis_type, gateway_latency_test_group_id, server_latency_test_group_id)  
                    VALUES (?, ?, ?, ?)                 
                """

            for diagnosis in diagnoses:
                params = (
                    diagnosis.date_time,
                    diagnosis.network_diagnosis_type.value,
                    diagnosis.gateway_latency_test_group_id,
                    diagnosis.server_latency_test_group_id,
                )

                cursor.execute(sql, params)

                if cursor.lastrowid is None:
                    raise Exception("Could not calculate latency_test_id")

                diagnosis.set_id(cursor.lastrowid)

                self._log_statement(
                    "ConnectionStatusDiagnosisRepository",
                    "_save_internal",
                    cursor,
                    {"sql": sql, "params": params},
                )
        except Exception as ex:
            raise DBOperationFailedException("ConnectionStatusDiagnosisRepository", "_save_internal", sql, params, str(ex))

    def _load_internal(
        self, cursor: Cursor, statement_addition: str = "", addition_placeholder_values: list[Any] = []
    ) -> list[ConnectionDiagnosis]:
        sql: str = ""
        try:
            sql: str = f"""
                SELECT id, date_time, network_diagnosis_type, gateway_latency_test_group_id, server_latency_test_group_id FROM connection_diagnoses {statement_addition}
            """

            cursor.execute(sql, addition_placeholder_values)
            rows: list[Any] = cursor.fetchall()

            self._log_statement(
                "ConnectionStatusDiagnosisRepository",
                "_load_internal",
                cursor,
                {"sql": sql, "params": {}, "row_count": len(rows)},
            )

            diagnoses: list[ConnectionDiagnosis] = []
            for id, date_time, network_diagnosis_type, gateway_latency_test_group_id, server_latency_test_group_id in rows:
                diagnoses.append(
                    ConnectionDiagnosis(
                        id, date_time, network_diagnosis_type, gateway_latency_test_group_id, None, server_latency_test_group_id, None
                    )
                )

            return diagnoses
        except Exception as ex:
            raise DBOperationFailedException("ConnectionStatusDiagnosisRepository", "_load_internal", sql, (), str(ex))

    def save(self, diagnoses: list[ConnectionDiagnosis]) -> None:
        self._database_manager.run_in_transaction(lambda cursor: self._save_internal(cursor, diagnoses))

    def load(self, statement_addition: str = "") -> list[ConnectionDiagnosis]:
        return self._database_manager.run_in_transaction(lambda cursor: self._load_internal(cursor, statement_addition))

    def load_latest(self) -> ConnectionDiagnosis | None:
        result: list[ConnectionDiagnosis] = self._database_manager.run_in_transaction(
            lambda cursor: self._load_internal(cursor, "ORDER BY date_time DESC LIMIT 1")
        )
        return result[0] if len(result) == 1 else None
