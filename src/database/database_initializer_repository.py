from database.base_repository import BaseRepository
from sqlite3 import Cursor


class DatabaseInitializerRepository(BaseRepository):

    # Initializes the database. If a table doesn't exists, it creates it.
    def _initialize_database_intern(self, cursor: Cursor) -> None:
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
            "DatabaseInitializerRepository",
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
            "DatabaseInitializerRepository",
            "initialize_database",
            cursor,
            {"sql": sql, "params": {}},
        )

        sql = """
            CREATE TABLE IF NOT EXISTS outages(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                connection_state TEXT NOT NULL,
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
        """
        cursor.execute(sql)
        self._log_statement(
            "DatabaseInitializerRepository",
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
                function_name TEXT NOT NULL,
                class_name TEXT NOT NULL,
                related_object_type TEXT,
                related_object_id INTEGER,
                details_json TEXT
            )           
        """
        cursor.execute(sql)
        self._log_statement(
            "DatabaseInitializerRepository",
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
            "DatabaseInitializerRepository",
            "initialize_database",
            cursor,
            {"sql": sql, "params": {}},
        )

    def initialize_database(self) -> None:
        self._database_manager.run_in_transaction(lambda cursor: self._initialize_database_intern(cursor))
