from runner import Runner
from config_manager import ConfigManager
from app_start_config import AppStartConfig
from database_manager import DatabaseManager
from app_logger import AppLogger
from models import LogType
from app_settings_manager import AppSettingsManager
from threading import Thread

if __name__ == "__main__":
    AppLogger.pre_initialize()
    
    settings_manager: AppSettingsManager | None = None
    runner_thread: Thread = Thread(target=Runner.run)
    try:
        config: AppStartConfig = ConfigManager.load_config()

        database_manager = DatabaseManager(config.database_config.path)
        database_manager.initialize_database()

        AppLogger.initialize(
            config.log_config.enabled_console_log_levels,
            config.log_config.enabled_database_log_levels,
            database_manager,
        )

        settings_manager = AppSettingsManager(database_manager)
        settings_manager.load_settings()

        AppLogger.info(LogType.SYSTEM, "Initialization completed", "main", "main")

        Runner.prepare(database_manager, settings_manager)

        runner_thread.start()
    except KeyboardInterrupt:
        if settings_manager is not None:
            settings_manager.save_settings()
            print("Program exited")

        Runner.stop()
        runner_thread.join()

    except Exception as ex:
        AppLogger.critical(LogType.SYSTEM, str(ex), "main", "main")
