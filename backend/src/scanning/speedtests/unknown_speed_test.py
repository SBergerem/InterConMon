# dummy class
from backend.src.scanning.speedtests.base_speed_test import BaseSpeedTest
from backend.src.models.models import SpeedTestResult, SpeedTestTool
from datetime import datetime


class UnknownSpeedTest(BaseSpeedTest):

    def _set_console_start_command(self) -> None:
        self._console_start_command = ""

    def execute(self) -> SpeedTestResult:
        return SpeedTestResult(
            0,
            datetime.now().isoformat(),
            False,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            "No speedtest tool configured",
            None,
            SpeedTestTool.UNKNOWN,
        )
