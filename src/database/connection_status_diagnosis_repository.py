from database.base_repository import BaseRepository
from sqlite3 import Cursor
from typing import Any
from models import ConnectionDiagnosis
from exceptions import DBOperationFailedException


class CpnnectionDiagnosisRepository(BaseRepository):

    def _save_internal(self, cursor: Cursor, diagnoses: list[ConnectionDiagnosis]) -> None:
        sql: str = ""
        params: tuple[str, str, int, int] = ("", "", 0, 0)
        try:
            sql = """
                    INSERT INTO connection_diagnoses (date_time, network_diagnsis_type, latency_test_group_id, outage_id)  
                    VALUES (?, ?, ?, ?)                 
                """

            for diagnosis in diagnoses:
                params = (diagnosis.date_time, diagnosis.network_diagnosis_type.value, diagnosis.latency_test_group_id, diagnosis.outage_id)

                cursor.execute(sql, params)

                if cursor.lastrowid is None:
                    raise Exception("Could not calculate latency_test_id")

                diagnosis.set_id(cursor.lastrowid)

                self._log_statement(
                    "CpnnectionStatusDiagnosisRepository",
                    "_save_internal",
                    cursor,
                    {"sql": sql, "params": params},
                )
        except Exception as ex:
            raise DBOperationFailedException("CpnnectionStatusDiagnosisRepository", "_save_internal", sql, params, str(ex))

    def _load_internal(self, cursor: Cursor, internal_where_statement: str = "") -> list[ConnectionDiagnosis]:
        sql: str = ""
        try:
            sql: str = f"""
                SELECT date_time, network_diagnosis_type, latency_test_group_id, outage_id FROM connection_diagnoses {internal_where_statement}
            """

            cursor.execute(sql)
            rows: list[Any] = cursor.fetchall()

            self._log_statement(
                "CpnnectionStatusDiagnosisRepository",
                "_load_internal",
                cursor,
                {"sql": sql, "params": {}, "row_count": len(rows)},
            )

            diagnoses: list[ConnectionDiagnosis] = []
            for id, date_time, network_diagnosis_type, latency_test_group_id, outage_id in rows:
                diagnoses.append(ConnectionDiagnosis(id, date_time, network_diagnosis_type, latency_test_group_id, None, outage_id, None))

            return diagnoses
        except Exception as ex:
            raise DBOperationFailedException("CpnnectionStatusDiagnosisRepository", "_load_internal", sql, (), str(ex))

    def save(self, diagnoses: list[ConnectionDiagnosis]) -> None:
        self._database_manager.run_in_transaction(lambda cursor: self._save_internal(cursor, diagnoses))

    def load(self, internal_where_statement: str = "") -> list[ConnectionDiagnosis]:
        return self._database_manager.run_in_transaction(lambda cursor: self._load_internal(cursor, internal_where_statement))
