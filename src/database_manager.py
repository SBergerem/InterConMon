from pathlib import Path
import sqlite3
from sqlite3 import Cursor
from outage_detector import OutageChangeState
from models import LatencyTestGroupResult, OutageDetectorResult, LogEntry, LogType
from app_logger import AppLogger


class DatabaseManager:

    def __init__(self, database_path: str) -> None:
        self._database_path = Path(database_path)
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: sqlite3.Connection | None = None

    def _open_connection(self) -> Cursor:
        self._connection = sqlite3.connect(self._database_path)
        cursor: Cursor = self._connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        return cursor

    def _close_connection(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def _log_statement(
        self, function_name: str, details: dict[str, object] | None = None
    ) -> None:
        AppLogger.extended_debug(
            LogType.DATABASE,
            "Executing SQL Statement",
            function_name,
            details=details,
        )

    def initialize_database(self) -> None:
        try:
            cursor: Cursor = self._open_connection()

            AppLogger.debug(
                LogType.DATABASE, "Starting SQL Transaction", "initialize_database"
            )

            if self._connection is None:
                AppLogger.error(
                    LogType.DATABASE,
                    "No connection to database",
                    "initialize_database",
                )
                return

            sql = """
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
                {"sql": sql, "params": {}},
            )

            self._connection.commit()

            AppLogger.debug(
                LogType.DATABASE, "Committing SQL Statements", "initialize_database"
            )
            AppLogger.debug(
                LogType.DATABASE, "Database initialized", "initialize_database"
            )
        finally:
            self._close_connection()

    def save_latency_test_group_result(
        self, latency_test_group_result: LatencyTestGroupResult
    ) -> int:
        group_id: int

        try:
            cursor: Cursor = self._open_connection()

            AppLogger.debug(
                LogType.DATABASE,
                "Starting SQL Transaction",
                "save_latency_test_group_result",
            )

            if self._connection is None:
                AppLogger.error(
                    LogType.DATABASE,
                    "No connection to database",
                    "save_latency_test_group_result",
                )
                return -1

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
            self._log_statement(
                "save_latency_test_group_result",
                {"sql": sql, "params": group_params},
            )

            group_id = cursor.lastrowid if cursor.lastrowid is not None else -1

            for single_test_result in latency_test_group_result.test_results:
                sql = """
                    INSERT INTO latency_tests (group_id, date_time, target, success, latency_ms, error_message)  
                    VALUES (?, ?, ?, ?, ?, ?)                 
                """

                single_params: tuple[int, str, str, int, float|None, str|None] = (
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
                    {"sql": sql, "params": single_params},
                )

            self._connection.commit()

            AppLogger.debug(
                LogType.DATABASE,
                "Committing SQL Statements",
                "save_latency_test_group_result",
            )
        except Exception as ex:
            if self._connection is not None:
                self._connection.rollback()

            AppLogger.error(
                LogType.DATABASE,
                str(ex),
                "save_latency_test_group_result",
            )

            raise ex
        finally:
            self._close_connection()

        return group_id

    def save_outage(self, outage_detection_result: OutageDetectorResult) -> int:
        if outage_detection_result.outage_change_state != OutageChangeState.ENDED.value:
            return -1

        try:
            cursor: Cursor = self._open_connection()

            AppLogger.debug(
                LogType.DATABASE,
                "Starting SQL Transaction",
                "save_outage",
            )

            if self._connection is None:
                AppLogger.error(
                    LogType.DATABASE,
                    "No connection to database",
                    "save_outage",
                )
                return -1

            sql = """
                INSERT INTO outages (start_time, end_time, duration_sec, started_group_id, ended_group_id)      
                VALUES (?, ?, ?, ?, ?)
            """

            params: tuple[
                str | None, str | None, float | None, int | None, int | None
            ] = (
                outage_detection_result.outage_start_time,
                outage_detection_result.outage_end_time,
                outage_detection_result.outage_duration_sec,
                outage_detection_result.outage_started_group_id,
                outage_detection_result.outage_ended_group_id,
            )

            cursor.execute(sql, params)
            self._log_statement(
                "save_outage",
                {"sql": sql, "params": params},
            )

            self._connection.commit()

            AppLogger.debug(
                LogType.DATABASE, "Committing SQL Statements", "save_outage"
            )

            return cursor.lastrowid if cursor.lastrowid is not None else -1
        except Exception as ex:
            if self._connection is not None:
                self._connection.rollback()

            AppLogger.error(
                LogType.DATABASE,
                str(ex),
                "save_outage",
            )

            raise ex
        finally:
            self._close_connection()

    # Can't log here, because it would result in log looping
    def save_log_entry(self, log_entry: LogEntry) -> None:
        try:
            cursor: Cursor = self._open_connection()

            if self._connection is None:
                return

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

            self._connection.commit()
        except Exception as ex:
            if self._connection is not None:
                self._connection.rollback()
            raise ex
        finally:
            self._close_connection()
