from app_logger import AppLogger
from models import LogType


class CustomException(Exception):
    def __init__(
        self,
        message: str,
        log_type: LogType,
        class_name: str,
        function_name: str,
        is_critical: bool = False,
    ) -> None:

        if is_critical:
            AppLogger.critical(
                log_type, message, class_name, function_name, skip_database=True
            )
        else:
            AppLogger.error(
                log_type, message, class_name, function_name, skip_database=True
            )

        super().__init__(message)


class DatabaseConnectionException(CustomException):
    def __init__(
        self,
        class_name: str,
        function_name: str,
        is_critical: bool = False,
    ) -> None:
        super().__init__(
            "No database connection", LogType.DATABASE, class_name, function_name
        )


class DBConIsNoneException(CustomException):
    def __init__(
        self,
        class_name: str,
        function_name: str,
        is_critical: bool = False,
    ) -> None:
        super().__init__(
            "No database connection", LogType.DATABASE, class_name, function_name
        )


class DBOperationFailedException(CustomException):
    def __init__(
        self,
        message: str,
        class_name: str,
        function_name: str,
        is_critical: bool = False,
    ) -> None:
        super().__init__(
            message,
            LogType.DATABASE,
            class_name,
            function_name,
        )
