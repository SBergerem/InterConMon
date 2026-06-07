from sqlite3 import Cursor
from exceptions import DBOperationFailedException
from database.database_manager import DatabaseManager


class BaseRepository:
    
    def __init__(self, database_manager: DatabaseManager)->None:
        self._database_manager: DatabaseManager = database_manager

    # Logs an sql statement, if called. So no need to write this extended_debug everywhere and the code is more readable
    def _log_statement(
        self,
        class_name: str,
        function_name: str,
        outer_cursor: Cursor,
        details: dict[str, object] | None = None,
    ) -> None:
        try:
        #AppLogger.extended_debug(
        #    LogType.DATABASE,
        #    "Executing SQL Statement",
        #    class_name,
        #    function_name,
        #    details=details,
        #    outer_cursor=outer_cursor,
        #)
            pass
        except Exception as ex:
            raise DBOperationFailedException(str(ex), "BaseRepository", "_log_statement")

    # Return a bool which tells if there is already a tuple with the primary key value, so an update method can be used instead an insert
    # Never use it outside of this class. SQL injection potential
    def _check_for_existing_tuple(
        self,
        class_name: str,
        table_name: str,
        column_name: str,
        primary_key_value: str | int,
        cursor: Cursor,
    ) -> bool:
        try:
            #AppLogger.debug(
            #    LogType.DATABASE,
            #    "Starting SQL Transaction",
            #    "DatabaseManager",
            #    "_check_for_existing_tuple",
            #    outer_cursor=cursor,
            #)

            sql: str = f"""
                SELECT 1 FROM {table_name} WHERE {column_name} = ? LIMIT 1
            """

            params: tuple[str | int] = (primary_key_value,)

            cursor.execute(sql, params)

            tuple_exists: bool = cursor.fetchone() is not None

            self._log_statement(
                class_name,
                "_check_for_existing_tuple",
                cursor,
                {"sql": sql, "params": params},
            )

            return tuple_exists
        except Exception as ex:
            raise DBOperationFailedException(str(ex), "BaseRepository", "_check_for_existing_tuple")
