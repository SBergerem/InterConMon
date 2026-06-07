from runner import Runner
from config_manager import ConfigManager
from app_start_config import AppStartConfig
from database.database_manager import DatabaseManager
from app_logger import AppLogger
from models import LogLevel, LogType
from app_settings import AppSettings
import time
from database.app_settings_repository import AppSettingsRepository
from database.database_initializer_repository import DatabaseInitializerRepository
from sqlite3 import Cursor


def log_database_statement(class_name: str, function_name: str, outer_cursor: Cursor, details: dict[str, object] | None = None) -> None:
    AppLogger.detailed_debug(
        LogType.DATABASE,
        "Executing SQL Statement",
        class_name,
        function_name,
        details=details,
        outer_cursor=outer_cursor,
    )


# Initializing all relevant managers, the start config and the logger and return the managers
def initialize_program() -> tuple[DatabaseManager, AppSettings]:
    AppLogger.pre_initialize()

    AppLogger.info(LogType.SYSTEM, "Starting Initialization", "", "initialize_program")

    config: AppStartConfig = ConfigManager.load_config()

    database_manager = DatabaseManager(config.database_config.path)
    database_manager.set_logging_callback(log_database_statement)
    database_initializer_repository: DatabaseInitializerRepository = DatabaseInitializerRepository(database_manager)
    database_initializer_repository.initialize_database()

    enabled_console_log_levels: list[LogLevel] = config.log_config.enabled_console_log_levels
    enabled_database_log_levels: list[LogLevel] = config.log_config.enabled_database_log_levels
    AppLogger.initialize(enabled_console_log_levels, enabled_database_log_levels, database_manager)

    app_settings_repository = AppSettingsRepository(database_manager)
    app_setting: AppSettings = app_settings_repository.load()

    AppLogger.info(LogType.SYSTEM, "Initialization complete", "", "initialize_program")

    return (database_manager, app_setting)


# Starting the initialization and after that the runner, which runs all available tests
# Program can be stopped, if the user sends a KeyboardInterrupt
if __name__ == "__main__":
    database_manager: DatabaseManager | None = None
    app_settings: AppSettings | None = None
    runner: Runner | None = None
    try:
        database_manager, app_settings = initialize_program()

        runner = Runner(database_manager, app_settings)
        runner.run()

        while runner.is_running():
            time.sleep(10)

    except KeyboardInterrupt:
        AppLogger.info(LogType.SYSTEM, "Keyboard interrupt. Program exiting..", "", "main")

        if runner is not None:
            runner.stop()

        if (app_settings is not None) and (database_manager is not None):
            app_settings_repository = AppSettingsRepository(database_manager)
            app_settings_repository.save(app_settings)
            AppLogger.info(LogType.SYSTEM, "Program exited", "", "main")

    except Exception as ex:
        AppLogger.critical(LogType.SYSTEM, str(ex), "", "main")
