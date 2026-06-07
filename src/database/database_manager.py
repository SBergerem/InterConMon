from pathlib import Path
import sqlite3
from sqlite3 import Cursor, Connection
from exceptions import DatabaseConnectionException
from threading import Lock
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


class DatabaseManager:

    def __init__(self, database_path: str) -> None:
        self._database_path = Path(database_path)
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock: Lock = Lock()
        self._logging_callback: Callable[[str, str, Cursor, dict[str, object] | None], None] | None = None

    # Opens a connection, enables foreign keys and return the connection, so everytime foreign keys are being use by sqlite
    def _open_connection(self) -> Connection:
        try:
            connection = sqlite3.connect(self._database_path, timeout=10)
            connection.execute("PRAGMA foreign_keys = ON")
            return connection
        except Exception as ex:
            raise DatabaseConnectionException("DatabaseManager", "_open_connection", str(ex))

    # Closes the connection if there is one. It is possible, to get no connection, if a function got an outer cursor
    # Than he isn't allowed to close the connection and this method gets None as connection
    def _close_connection(self, connection: Connection | None) -> None:
        if connection is not None:
            connection.close()

    # Callback for logging. If not set, the program just dont log database transactions
    def set_logging_callback(self, callback: Callable[[str, str, Cursor, dict[str, object] | None], None]) -> None:
        self._logging_callback = callback

    # Callback for the repositories. With this callback, they get an cursor and are locking the connection
    def run_in_transaction(self, callback: Callable[[Cursor], T], outer_cursor: Cursor | None = None) -> T:
        if outer_cursor is not None:
            return callback(outer_cursor)

        connection: Connection | None = None

        with self._lock:
            try:
                connection = self._open_connection()
                cursor: Cursor = connection.cursor()

                result: T = callback(cursor)

                connection.commit()

                return result
            except Exception:
                if connection is not None:
                    connection.rollback()
                raise

            finally:
                self._close_connection(connection)

    # Logs an sql statement, if called. So no need to write this extended_debug everywhere and the code is more readable
    def log_statement(
        self,
        class_name: str,
        function_name: str,
        outer_cursor: Cursor,
        details: dict[str, object] | None = None,
    ) -> None:
        if self._logging_callback is None:
            return

        self._logging_callback(class_name, function_name, outer_cursor, details)
