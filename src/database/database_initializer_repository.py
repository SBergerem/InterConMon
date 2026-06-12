from database.base_repository import BaseRepository
from sqlite3 import Cursor
from exceptions import DBOperationFailedException


class DatabaseInitializerRepository(BaseRepository):

    def _execute_sql_statement(self, statement: str, cursor: Cursor) -> None:
        cursor.execute(statement)

        self._log_statement(
            "DatabaseInitializerRepository",
            "_execute_sql_statement",
            cursor,
            {"sql": statement, "params": {}},
        )

    # Initializes the database. If a table doesn't exists, it creates it.
    def _initialize_database_intern(self, cursor: Cursor) -> None:
        sql: str = ""
        try:
            self._execute_sql_statement(
                """ CREATE TABLE IF NOT EXISTS latency_test_groups(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        start_time TEXT NOT NULL,
                        end_time TEXT NOT NULL,
                        time_needed_sec REAL NOT NULL,
                        any_success INTEGER NOT NULL,
                        group_success INTEGER NOT NULL,
                        test_target_type TEXT NOT NULL 
                )
            """,
                cursor,
            )

            self._execute_sql_statement(
                """ CREATE TABLE IF NOT EXISTS latency_tests(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        group_id INTEGER NOT NULL,
                        date_time TEXT NOT NULL,
                        target TEXT NOT NULL,
                        test_target_type TEXT NOT NULL,
                        success INTEGER NOT NULL,
                        latency_ms REAL,
                        error_message TEXT,
                        
                        FOREIGN KEY (group_id) REFERENCES latency_test_groups(id)
                        ON DELETE CASCADE
                )               
            """,
                cursor,
            )

            self._execute_sql_statement(
                """ CREATE TABLE IF NOT EXISTS outages(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        reachability_state TEXT NOT NULL,
                        test_target_type TEXT NOT NULL,
                        last_connection_test TEXT NOT NULL,
                        change_state TEXT NOT NULL,
                        start_time TEXT NOT NULL,
                        end_time TEXT NOT NULL,
                        duration_sec REAL NOT NULL,
                        started_group_id INTEGER NOT NULL,
                        ended_group_id INTEGER NOT NULL,
                        
                        FOREIGN KEY (started_group_id) REFERENCES latency_test_groups(id),
                        FOREIGN KEY (ended_group_id) REFERENCES latency_test_groups(id)
                )
            """,
                cursor,
            )

            self._execute_sql_statement(
                """ CREATE TABLE IF NOT EXISTS connection_diagnoses(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date_time TEXT NOT NULL,
                        network_diagnosis_type TEXT NOT NULL,
                        gateway_latency_test_group_id INTEGER NOT NULL, 
                        server_latency_test_group_id INTEGER NOT NULL,
                        
                        FOREIGN KEY (gateway_latency_test_group_id) REFERENCES latency_test_groups(id),
                        FOREIGN KEY (server_latency_test_group_id) REFERENCES latency_test_groups(id)
                )
            """,
                cursor,
            )

            self._execute_sql_statement(
                """ CREATE TABLE IF NOT EXISTS logs(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date_time TEXT NOT NULL,
                        log_level TEXT NOT NULL,
                        log_type TEXT NOT NULL,
                        log_message TEXT NOT NULL,
                        function_name TEXT NOT NULL,
                        class_name TEXT NOT NULL,
                        related_object_type TEXT,
                        related_object_id INTEGER,
                        details_json TEXT
                )           
            """,
                cursor,
            )

            self._execute_sql_statement(
                """ CREATE TABLE IF NOT EXISTS app_settings(
                        settings_name TEXT PRIMARY KEY,
                        settings_json TEXT NOT NULL,
                        changed_at TEXT NOT NULL
                )
            """,
                cursor,
            )

            self._execute_sql_statement(
                """ CREATE TABLE IF NOT EXISTS speed_test_results(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date_time TEXT NOT NULL,
                        success INTEGER NOT NULL,
                        download_mbps REAL,
                        upload_mbps REAL,
                        ping_ms REAL,
                        jitter_ms REAL,
                        server_name TEXT,
                        server_location TEXT,
                        server_id INTEGER,
                        server_url TEXT,
                        isp TEXT,
                        external_ip TEXT,
                        error_message TEXT,
                        duration_sec REAL,
                        tool_name TEST NOT NULL
                )
            """,
                cursor,
            )

        except Exception as ex:
            raise DBOperationFailedException("DatabaseInitializerRepository", "_initialize_database_intern", sql, (), str(ex))

    def initialize_database(self) -> None:
        self._database_manager.run_in_transaction(lambda cursor: self._initialize_database_intern(cursor))
