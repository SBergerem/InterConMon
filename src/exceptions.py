from models import LogType


class CustomException(Exception):
    def __init__(
        self,
        message: str,
        log_type: LogType,
        class_name: str,
        function_name: str,
        is_critical: bool = False,
        exception_name: str = "Custom exception (General)",
    ) -> None:

        # if is_critical:
        # AppLogger.critical(
        #    log_type,
        #    f"[{exception_name}] -> {message}",
        #    class_name,
        #    function_name,
        #    skip_database=True,
        # )
        # else:
        # AppLogger.error(
        #    log_type,
        #    f"[{exception_name}] -> {message}",
        #    class_name,
        #    function_name,
        #    skip_database=True,
        # )

        super().__init__(message)


class DatabaseConnectionException(CustomException):
    def __init__(
        self,
        class_name: str,
        function_name: str,
        is_critical: bool = False,
    ) -> None:
        super().__init__(
            "No database connection",
            LogType.DATABASE,
            class_name,
            function_name,
            exception_name="DatabaseConnectionException",
            is_critical=is_critical,
        )


class DBConIsNoneException(CustomException):
    def __init__(
        self,
        class_name: str,
        function_name: str,
        is_critical: bool = False,
    ) -> None:
        super().__init__(
            "No database connection",
            LogType.DATABASE,
            class_name,
            function_name,
            exception_name="DBConIsNoneException",
            is_critical=is_critical,
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
            message, LogType.DATABASE, class_name, function_name, exception_name="DBOperationFailedException", is_critical=is_critical
        )


class ObjectIsNoneException(CustomException):
    def __init__(
        self,
        object_name: str,
        object_type: str,
        log_type: LogType,
        class_name: str,
        function_name: str,
        is_critical: bool = False,
    ) -> None:
        super().__init__(
            f"Object {object_name} of type {object_type} is None",
            log_type,
            class_name,
            function_name,
            is_critical=is_critical,
            exception_name="ObjectIsNoneException",
        )


class ObjectIsNotPreparedException(CustomException):
    def __init__(
        self,
        object_name: str,
        object_type: str,
        log_type: LogType,
        class_name: str,
        function_name: str,
        is_critical: bool = False,
    ) -> None:
        super().__init__(
            f"Can't execute function. Object {object_name} of type {object_type} is not prepared",
            log_type,
            class_name,
            function_name,
            is_critical=is_critical,
            exception_name="ObjectIsNotPreparedException",
        )


class ThreadIsAlreadyRunningException(CustomException):
    def __init__(
        self,
        object_name: str,
        object_type: str,
        log_type: LogType,
        class_name: str,
        function_name: str,
        is_critical: bool = False,
    ) -> None:
        super().__init__(
            f"Can't start thread. Object {object_name} of type {object_type} is already running as thread",
            log_type,
            class_name,
            function_name,
            is_critical=is_critical,
            exception_name="ThreadIsAlreadyRunningException",
        )


class ThreadStoppedException(CustomException):
    def __init__(
        self,
        log_type: LogType,
        class_name: str,
        function_name: str,
        is_critical: bool = False,
    ) -> None:
        super().__init__(
            f"Thread stopped",
            log_type,
            class_name,
            function_name,
            is_critical=is_critical,
            exception_name="ThreadStoppedException",
        )
