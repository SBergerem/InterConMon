# dummy class
from speedtests.base_speed_test import BaseSpeedTest
from models import SpeedTestResult, SpeedTestTool
from datetime import datetime


class UnknownSpeedTest(BaseSpeedTest):

    def _is_cli_available(self) -> bool:
        return super()._is_cli_available()

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
            "No speedtest tool configured",
            None,
            SpeedTestTool.UNKNOWN,
        )
