from pathlib import Path
import sqlite3
from sqlite3 import Cursor, Connection
from typing import Any
from outage_detector import OutageChangeState
from models import LatencyTestGroupResult, OutageDetectorResult, LogEntry, LogType
from app_logger import AppLogger
import json
from datetime import datetime
from exceptions import (
    DatabaseConnectionException,
    DBConIsNoneException,
    DBOperationFailedException,
)


class DatabaseManager:

    def __init__(self, database_path: str) -> None:
        self._database_path = Path(database_path)
        self._database_path.parent.mkdir(parents=True, exist_ok=True)

    def _open_connection(self) -> Connection:
        try:
            connection = sqlite3.connect(self._database_path, timeout=10)
            connection.execute("PRAGMA foreign_keys = ON")
            return connection
        except Exception:
            raise DatabaseConnectionException("DatabaseManager", "_open_connection", True)

    def _close_connection(self, connection: Connection | None) -> None:
        if connection is not None:
            connection.close()

    def _log_statement(
        self,
        function_name: str,
        outer_cursor: Cursor,
        details: dict[str, object] | None = None,
    ) -> None:
        AppLogger.extended_debug(
            LogType.DATABASE,
            "Executing SQL Statement",
            "DatabaseManager",
            function_name,
            details=details,
            outer_cursor=outer_cursor,
        )

    def _check_for_existing_tuple(
        self,
        table_name: str,
        column_name: str,
        primary_key_value: str | int,
        outer_cursor: Cursor | None = None,
    ) -> bool:
        connection: Connection | None = None
        try:
            if outer_cursor is None:
                connection = self._open_connection()
                cursor: Cursor = connection.cursor()
            else:
                cursor = outer_cursor

            AppLogger.debug(
                LogType.DATABASE,
                "Starting SQL Transaction",
                "DatabaseManager",
                "_check_for_existing_tuple",
                outer_cursor=cursor,
            )

            sql: str = f"""
                SELECT 1 FROM {table_name} WHERE {column_name} = ? LIMIT 1
            """

            params: tuple[str | int] = (primary_key_value,)

            tuple_exists: bool = cursor.fetchone() is not None

            cursor.execute(sql, params)
            self._log_statement(
                "_check_for_existing_tuple",
                cursor,
                {"sql": sql, "params": params},
            )

            return tuple_exists
        except Exception as ex:
            raise DBOperationFailedException(str(ex), "DatabaseManager", "_check_for_existing_tuple")
        finally:
            if outer_cursor is None:
                self._close_connection(connection)

    def initialize_database(self) -> None:
        connection: Connection | None = None
        try:
            connection = self._open_connection()
            cursor: Cursor = connection.cursor()

            AppLogger.debug(
                LogType.DATABASE,
                "Starting SQL Transaction",
                "DatabaseManager",
                "initialize_database",
                outer_cursor=cursor,
            )

            sql: str = """
                CREATE TABLE IF NOT EXISTS latency_test_groups(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    time_needed_sec REAL NOT NULL,
                    any_success INTEGER NOT NULL,
                    group_success INTEGER NOT NULL 
                )
            """
            cursor.execute(sql)
            self._log_statement(
                "initialize_database",
                cursor,
                {"sql": sql, "params": {}},
            )

            sql = """
                CREATE TABLE IF NOT EXISTS latency_tests(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    date_time TEXT NOT NULL,
                    target TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    latency_ms REAL,
                    error_message TEXT,
                    
                    FOREIGN KEY (group_id) REFERENCES latency_test_groups(id)
                    ON DELETE CASCADE
                )               
            """
            cursor.execute(sql)
            self._log_statement(
                "initialize_database",
                cursor,
                {"sql": sql, "params": {}},
            )

            sql = """
                CREATE TABLE IF NOT EXISTS outages(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    duration_sec REAL NOT NULL,
                    started_group_id INTEGER NOT NULL,
                    ended_group_id INTEGER NOT NULL,
                    
                    FOREIGN KEY (started_group_id) REFERENCES latency_test_groups(id),
                    FOREIGN KEY (ended_group_id) REFERENCES latency_test_groups(id)
                )
            """
            cursor.execute(sql)
            self._log_statement(
                "initialize_database",
                cursor,
                {"sql": sql, "params": {}},
            )

            sql = """
                CREATE TABLE IF NOT EXISTS logs(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date_time TEXT NOT NULL,
                    log_level TEXT NOT NULL,
                    log_type TEXT NOT NULL,
                    log_message TEXT NOT NULL,
                    related_object_type TEXT,
                    related_object_id INTEGER,
                    details_json TEXT
                )           
            """
            cursor.execute(sql)
            self._log_statement(
                "initialize_database",
                cursor,
                {"sql": sql, "params": {}},
            )

            sql = """
                CREATE TABLE IF NOT EXISTS app_settings(
                    settings_name TEXT PRIMARY KEY,
                    settings_json TEXT NOT NULL,
                    changed_at TEXT NOT NULL
                )
            """
            cursor.execute(sql)
            self._log_statement(
                "initialize_database",
                cursor,
                {"sql": sql, "params": {}},
            )

            connection.commit()

            AppLogger.debug(
                LogType.DATABASE,
                "Committing SQL Statements",
                "DatabaseManager",
                "initialize_database",
                outer_cursor=cursor,
            )
            AppLogger.debug(
                LogType.DATABASE,
                "Database initialized",
                "DatabaseManager",
                "initialize_database",
                outer_cursor=cursor,
            )
        except Exception as ex:
            raise DBOperationFailedException(str(ex), "DatabaseManager", "initialize_database")
        finally:
            self._close_connection(connection)

    def save_latency_test_group_result(self, latency_test_group_result: LatencyTestGroupResult) -> int:
        group_id: int

        connection: Connection | None = None
        try:
            connection = self._open_connection()
            cursor: Cursor = connection.cursor()

            AppLogger.debug(
                LogType.DATABASE,
                "Starting SQL Transaction",
                "DatabaseManager",
                "save_latency_test_group_result",
                outer_cursor=cursor,
            )

            sql = """
                    INSERT INTO latency_test_groups (start_time, end_time, time_needed_sec, any_success, group_success) 
                    VALUES (?, ?, ?, ?, ?)
            """

            group_params: tuple[str | None, str, float | None, int, int] = (
                latency_test_group_result.start_time,
                latency_test_group_result.end_time,
                latency_test_group_result.time_needed_sec,
                int(latency_test_group_result.any_success),
                int(latency_test_group_result.group_success),
            )

            cursor.execute(sql, group_params)

            group_id = cursor.lastrowid if cursor.lastrowid is not None else -1

            self._log_statement(
                "save_latency_test_group_result",
                cursor,
                {"sql": sql, "params": group_params},
            )

            for single_test_result in latency_test_group_result.test_results:
                sql = """
                    INSERT INTO latency_tests (group_id, date_time, target, success, latency_ms, error_message)  
                    VALUES (?, ?, ?, ?, ?, ?)                 
                """

                single_params: tuple[int, str, str, int, float | None, str | None] = (
                    group_id,
                    single_test_result.date_time,
                    single_test_result.target,
                    int(single_test_result.success),
                    single_test_result.latency_ms,
                    single_test_result.error_message,
                )

                cursor.execute(sql, single_params)
                self._log_statement(
                    "save_latency_test_group_result",
                    cursor,
                    {"sql": sql, "params": single_params},
                )

            connection.commit()

            AppLogger.debug(
                LogType.DATABASE,
                "Committing SQL Statements",
                "DatabaseManager",
                "save_latency_test_group_result",
                outer_cursor=cursor,
            )
        except Exception as ex:
            if connection is not None:
                connection.rollback()

            raise DBOperationFailedException(str(ex), "DatabaseManager", "save_latency_test_group_result")
        finally:
            self._close_connection(connection)

        return group_id

    def save_outage(self, outage_detection_result: OutageDetectorResult) -> int:
        if outage_detection_result.outage_change_state != OutageChangeState.ENDED.value:
            return -1

        connection: Connection | None = None
        try:
            connection = self._open_connection()
            cursor: Cursor = connection.cursor()

            AppLogger.debug(
                LogType.DATABASE,
                "Starting SQL Transaction",
                "DatabaseManager",
                "save_outage",
                outer_cursor=cursor,
            )

            sql = """
                INSERT INTO outages (start_time, end_time, duration_sec, started_group_id, ended_group_id)      
                VALUES (?, ?, ?, ?, ?)
            """

            params: tuple[str | None, str | None, float | None, int | None, int | None] = (
                outage_detection_result.outage_start_time,
                outage_detection_result.outage_end_time,
                outage_detection_result.outage_duration_sec,
                outage_detection_result.outage_started_group_id,
                outage_detection_result.outage_ended_group_id,
            )

            cursor.execute(sql, params)
            self._log_statement(
                "save_outage",
                cursor,
                {"sql": sql, "params": params},
            )

            connection.commit()

            outage_id: int = cursor.lastrowid if cursor.lastrowid is not None else -1

            AppLogger.debug(
                LogType.DATABASE,
                "Committing SQL Statements",
                "DatabaseManager",
                "save_outage",
                outer_cursor=cursor,
            )

            return outage_id
        except Exception as ex:
            if connection is not None:
                connection.rollback()

            raise DBOperationFailedException(str(ex), "DatabaseManager", "save_outage")
        finally:
            self._close_connection(connection)

    # Can't log here, because it would result in log looping
    def save_log_entry(self, log_entry: LogEntry, outer_cursor: Cursor | None = None) -> None:
        connection: Connection | None = None
        try:
            if outer_cursor is None:
                connection = self._open_connection()
                cursor: Cursor = connection.cursor()
            else:
                cursor = outer_cursor

            sql = """
                   INSERT INTO logs (date_time, log_level, log_type, log_message, related_object_type, related_object_id, details_json)        
                   VALUES (?, ?, ?, ?, ?, ?, ?)
            """

            params: tuple[str, str, str, str, str | None, int | None, str | None] = (
                log_entry.date_time,
                log_entry.log_level.value,
                log_entry.log_type.value,
                log_entry.log_message,
                log_entry.related_object_type,
                log_entry.related_object_id,
                log_entry.details_json,
            )

            cursor.execute(sql, params)

            if outer_cursor is None and connection is not None:
                connection.commit()
        except DBConIsNoneException:
            raise
        except Exception as ex:
            if connection is not None:
                connection.rollback()

            raise DBOperationFailedException(str(ex), "DatabaseManager", "save_log_entry")
        finally:
            if outer_cursor is None:
                self._close_connection(connection)

    def save_settings(self, tuples_to_save: list[tuple[str, object]]) -> None:
        connection: Connection | None = None
        try:
            connection = self._open_connection()
            cursor: Cursor = connection.cursor()

            for setting_name, settings in tuples_to_save:
                if self._check_for_existing_tuple("app_settings", "settings_name", setting_name, cursor):
                    sql = """
                        UPDATE app_settings SET settings_json = ?, changed_at = ? WHERE settings_name = ?
                    """

                    params = (
                        json.dumps(settings),
                        datetime.now().isoformat(),
                        setting_name,
                    )

                    cursor.execute(sql, params)
                    self._log_statement(
                        "save_settings",
                        cursor,
                        {"sql": sql, "params": params},
                    )
                else:
                    sql = """
                        INSERT INTO app_settings (settings_name, settings_json, changed_at)
                        VALUES (?, ?, ?)
                    """

                    params = (
                        setting_name,
                        json.dumps(settings),
                        datetime.now().isoformat(),
                    )

                    cursor.execute(sql, params)
                    self._log_statement(
                        "save_settings",
                        cursor,
                        {"sql": sql, "params": params},
                    )

            connection.commit()
        except Exception as ex:
            if connection is not None:
                connection.rollback()

            raise DBOperationFailedException(str(ex), "DatabaseManager", "save_settings")
        finally:
            self._close_connection(connection)

    def load_settings(self) -> list[tuple[str, str]]:
        connection: Connection | None = None
        try:
            connection = self._open_connection()
            cursor: Cursor = connection.cursor()

            AppLogger.debug(
                LogType.DATABASE,
                "Starting SQL Transaction",
                "DatabaseManager",
                "load_settings",
                outer_cursor=cursor,
            )

            sql: str = """
                SELECT settings_name, settings_json FROM app_settings
            """

            cursor.execute(sql)
            rows: list[Any] = cursor.fetchall()

            self._log_statement(
                "load_settings",
                cursor,
                {"sql": sql, "params": {}, "row_count": len(rows)},
            )

            result: list[tuple[str, str]] = []
            for settings_name, settings_json in rows:
                result.append((settings_name, settings_json))

            return result

        except Exception as ex:
            raise DBOperationFailedException(str(ex), "DatabaseManager", "load_settings")
        finally:
            self._close_connection(connection)
