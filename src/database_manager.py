from pathlib import Path
import sqlite3
from outage_detector import OutageChangeState


class DatabaseManager:

    def __init__(self, database_path):
        self._database_path = Path(database_path)
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = None

    def _open_connection(self):
        self._connection = sqlite3.connect(self._database_path)
        cursor = self._connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        return cursor

    def _close_connection(self):
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def initialize_database(self):
        try:
            cursor = self._open_connection()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS latency_test_groups(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    time_needed_sec REAL NOT NULL,
                    any_success INTEGER NOT NULL,
                    group_success INTEGER NOT NULL 
                )
            """)

            cursor.execute("""
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
            """)

            cursor.execute("""
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
            """)

            cursor.execute("""
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
            """)

            self._connection.commit()
        finally:
            self._close_connection()

    def save_latency_test_group_result(self, latency_test_group_result):
        group_id = None

        try:
            cursor = self._open_connection()

            cursor.execute(
                """
                INSERT INTO latency_test_groups (start_time, end_time, time_needed_sec, any_success, group_success) 
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    latency_test_group_result.start_time,
                    latency_test_group_result.end_time,
                    latency_test_group_result.time_needed_sec,
                    int(latency_test_group_result.any_success),
                    int(latency_test_group_result.group_success),
                ),
            )

            group_id = cursor.lastrowid

            for single_test_result in latency_test_group_result.test_results:
                cursor.execute(
                    """
                    INSERT INTO latency_tests (group_id, date_time, target, success, latency_ms, error_message)  
                    VALUES (?, ?, ?, ?, ?, ?)                 
                    """,
                    (
                        group_id,
                        single_test_result.date_time,
                        single_test_result.target,
                        int(single_test_result.success),
                        single_test_result.latency_ms,
                        single_test_result.error_message,
                    ),
                )

            self._connection.commit()
        except Exception as ex:
            if self._connection is not None:
                self._connection.rollback()
            raise ex
        finally:
            self._close_connection()

        return group_id

    def save_outage(self, outage_data):
        if outage_data.outage_change_state != OutageChangeState.ENDED.value:
            return

        try:
            cursor = self._open_connection()

            cursor.execute(
                """
                INSERT INTO outages (start_time, end_time, duration_sec, started_group_id, ended_group_id)      
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    outage_data.outage_start_time,
                    outage_data.outage_end_time,
                    outage_data.outage_duration_sec,
                    outage_data.outage_started_group_id,
                    outage_data.outage_ended_group_id,
                ),
            )

            self._connection.commit()
        except Exception as ex:
            if self._connection is not None:
                self._connection.rollback()
            raise ex
        finally:
            self._close_connection()

    def save_log_entry(self, log_entry):
        try:
            cursor = self._open_connection()

            cursor.execute(
                """
                   INSERT INTO logs (date_time, log_level, log_type, log_message, related_object_type, related_object_id, details_json)        
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    log_entry.date_time,
                    log_entry.log_level,
                    log_entry.log_type,
                    log_entry.log_message,
                    log_entry.related_object_type,
                    log_entry.related_object_id,
                    log_entry.details_json,
                ),
            )
            
            self._connection.commit()
        except Exception as ex:
            if self._connection is not None:
                self._connection.rollback()
            raise ex
        finally:
            self._close_connection()
