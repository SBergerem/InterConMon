from abc import ABC, abstractmethod
from models import SpeedTestResult, LogType
from app_settings import SpeedTestSettings
import subprocess
from exceptions import CLICommandException
from app_logger import AppLogger
import shutil


class BaseSpeedTest(ABC):

    def __init__(self, settings: SpeedTestSettings) -> None:
        self._settings: SpeedTestSettings = settings
        self._console_start_command: str = ""
        self._set_console_start_command()

    @abstractmethod
    def _set_console_start_command(self) -> None:
        pass

    def _execute_command(self, command: list[str]) -> tuple[bool, str, str]:
        complete_command: list[str] = []
        try:
            complete_command = [self._console_start_command] + command

            AppLogger.debug(LogType.SCAN, "Starting speedtest. This takes some time..", "BaseSpeedTest", "_execute_command")

            result: subprocess.CompletedProcess[str] = subprocess.run(
                complete_command, capture_output=True, text=True, timeout=self._settings.get_max_duration_sec()
            )

            AppLogger.debug(LogType.SCAN, f"Speedtest finished with return code {result.returncode}", "BaseSpeedTest", "_execute_command")

            print(result.returncode)
            print(result.stderr)
            print(result.stdout)

            return (result.returncode == 0, result.stdout, result.stderr)
        except Exception as ex:
            raise CLICommandException("BaseSpeedTest", "_execute_command", str(ex), " ".join(complete_command))

    def _is_cli_available(self, name: str) -> bool:
        return shutil.which(name) is not None

    @abstractmethod
    def execute(self) -> SpeedTestResult:
        pass
