from abc import ABC, abstractmethod
from models import SpeedTestResult


class BaseSpeedTest(ABC):

    @abstractmethod
    def _is_cli_available(self) -> bool:
        return True

    @abstractmethod
    def execute(self) -> SpeedTestResult:
        pass
