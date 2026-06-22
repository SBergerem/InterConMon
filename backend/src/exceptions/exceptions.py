from typing import Any


class CustomException(Exception):
    def __init__(
        self,
        class_name: str,
        function_name: str,
        message: str,
        exception_name: str = "Custom exception (General)",
    ) -> None:
        self.class_name: str = class_name
        self.function_name: str = function_name
        super().__init__(f"[{exception_name}] -> {message}")


class DatabaseConnectionException(CustomException):
    def __init__(self, class_name: str, function_name: str, message: str) -> None:
        super().__init__(
            class_name,
            function_name,
            f"Database connection error. \n    Reason: {message}",
            exception_name="DatabaseConnectionException",
        )


class DBConIsNoneException(CustomException):
    def __init__(self, class_name: str, function_name: str) -> None:
        super().__init__(
            class_name,
            function_name,
            f"No Database connection",
            exception_name="DBConIsNoneException",
        )


class DBOperationFailedException(CustomException):
    def __init__(self, class_name: str, function_name: str, sql: str, params: Any, message: str) -> None:

        sql = " ".join(sql.split())

        super().__init__(
            class_name,
            function_name,
            f"SQL operation failed! \n    SQL: {sql} \n    Params: {params} \n    Reason: {message}",
            exception_name="DBOperationFailedException",
        )


class ObjectIsNoneException(CustomException):
    def __init__(self, class_name: str, function_name: str, object_name: str, object_type: str) -> None:
        super().__init__(
            class_name,
            function_name,
            f"Object {object_name} of type {object_type} is None",
            exception_name="ObjectIsNoneException",
        )


class ListIsEmptyException(CustomException):
    def __init__(self, class_name: str, function_name: str, object_name: str, object_type: str) -> None:
        super().__init__(
            class_name,
            function_name,
            f"List {object_name} of type {object_type} is empty",
            exception_name="ObjectIsNoneException",
        )


class ObjectIsNotPreparedException(CustomException):
    def __init__(self, class_name: str, function_name: str, object_name: str, object_type: str) -> None:
        super().__init__(
            class_name,
            function_name,
            f"Can't execute function. Object {object_name} of type {object_type} is not prepared",
            exception_name="ObjectIsNotPreparedException",
        )


class ThreadIsAlreadyRunningException(CustomException):
    def __init__(self, class_name: str, function_name: str, thread_name: str) -> None:
        super().__init__(
            class_name,
            function_name,
            f"Can't start thread {thread_name}. It is already running",
            exception_name="ThreadIsAlreadyRunningException",
        )


class ThreadStoppedException(CustomException):
    def __init__(self, class_name: str, function_name: str, thread_name: str) -> None:
        super().__init__(
            class_name,
            function_name,
            f"Thread {thread_name} stopped",
            exception_name="ThreadStoppedException",
        )


class ValueInvalidException(CustomException):
    def __init__(self, class_name: str, function_name: str, value: Any, message: str) -> None:
        super().__init__(
            class_name,
            function_name,
            f"Can't set value {value}. \n    Reason: {message} ",
            exception_name="ValueInvalidException",
        )


class MethodNotImplementedException(CustomException):
    def __init__(self, class_name: str, function_name: str) -> None:
        super().__init__(
            class_name,
            function_name,
            f"Function {function_name} in class {class_name} is not implemented!",
            exception_name="MethodNotImplementedException",
        )


class CLINotInstalledException(CustomException):
    def __init__(self, cli_name: str, class_name: str, function_name: str) -> None:
        super().__init__(
            class_name,
            function_name,
            f"The configured CLI ({cli_name}) is not available. Please install it and try again, or choose an other CLI.",
            exception_name="CLINotInstalledException",
        )


class CLICommandException(CustomException):
    def __init__(self, class_name: str, function_name: str, message: str, command: str) -> None:
        super().__init__(
            class_name,
            function_name,
            f"Error while executing the command ({command}). Reason: {message}.",
            exception_name="CLICommandException",
        )
