from database.base_repository import BaseRepository
from sqlite3 import Cursor
from models import SpeedTestResult
from typing import Any
from exceptions import DBOperationFailedException


class SpeedTestResultRepository(BaseRepository):

    def _save_internal(self, cursor: Cursor, results: list[SpeedTestResult]) -> None:
        sql: str = ""
        params: tuple[
            str,
            bool,
            float | None,
            float | None,
            float | None,
            float | None,
            str | None,
            str | None,
            int | None,
            str | None,
            str | None,
            str | None,
            str | None,
            float | None,
            str,
        ] = ("", False, None, None, None, None, None, None, None, None, None, None, None, None, "")
        try:
            sql = """
                INSERT INTO speed_test_results (date_time, success, download_mbps, upload_mbps, ping_ms, jitter_ms, server_name, 
                server_location, server_id, server_url, isp, external_ip, error_message, duration_sec, tool_name) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            for result in results:
                params = (
                    result.date_time,
                    result.success,
                    result.download_mbps,
                    result.upload_mbps,
                    result.ping_ms,
                    result.jitter_ms,
                    result.server_name,
                    result.server_location,
                    result.server_id,
                    result.server_url,
                    result.isp,
                    result.external_ip,
                    result.error_message,
                    result.duration_sec,
                    result.tool.value,
                )

                cursor.execute(sql, params)

                if cursor.lastrowid is None:
                    raise Exception("Could not calculate id.")

                result.set_id(cursor.lastrowid)

                self._log_statement(
                    "SpeedTestResultRepository",
                    "_save_internal",
                    cursor,
                    {"sql": sql, "params": params},
                )
        except Exception as ex:
            raise DBOperationFailedException("SpeedTestResultRepository", "_save_internal", sql, params, str(ex))

    def _load_internal(self, cursor: Cursor, internal_where_statement: str = "") -> list[SpeedTestResult]:
        sql: str = ""
        try:
            sql = f""" 
                SELECT id, date_time, success, download_mbps, upload_mbps, ping_ms, jitter_ms, server_name, 
                server_location, server_id, server_url, isp, external_ip, error_message, duration_sec, tool_name 
                FROM speed_test_results {internal_where_statement}
            """

            cursor.execute(sql)
            rows: list[Any] = cursor.fetchall()

            self._log_statement(
                "LatencyTestRepository",
                "_load_internal",
                cursor,
                {"sql": sql, "params": {}, "row_count": len(rows)},
            )

            results: list[SpeedTestResult] = []
            for (
                id,
                date_time,
                success,
                download_mbps,
                upload_mbps,
                ping_ms,
                jitter_ms,
                server_name,
                server_location,
                server_id,
                server_url,
                isp,
                external_ip,
                error_message,
                duration_sec,
                tool_name,
            ) in rows:
                results.append(
                    SpeedTestResult(
                        id,
                        date_time,
                        success,
                        download_mbps,
                        upload_mbps,
                        ping_ms,
                        jitter_ms,
                        server_name,
                        server_location,
                        server_id,
                        server_url,
                        isp,
                        external_ip,
                        error_message,
                        duration_sec,
                        tool_name,
                    )
                )

            return results
        except Exception as ex:
            raise DBOperationFailedException("SpeedTestResultRepository", "_load_internal", sql, (), str(ex))

    def save(self, results: list[SpeedTestResult]) -> None:
        return self._database_manager.run_in_transaction(lambda cursor: self._save_internal(cursor, results))

    def load(self, internal_where_statement: str = "") -> list[SpeedTestResult]:
        return self._database_manager.run_in_transaction(lambda cursor: self._load_internal(cursor, internal_where_statement))
