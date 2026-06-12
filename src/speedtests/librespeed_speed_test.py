from speedtests.base_speed_test import BaseSpeedTest
from models import SpeedTestResult, SpeedTestTool
from exceptions import CLINotInstalledException
from datetime import datetime
import json
from typing import Any
import time


class LibreSpeedSpeedTest(BaseSpeedTest):

    def _set_console_start_command(self) -> None:
        self._console_start_command = "librespeed-cli"

    def _is_cli_available(self) -> bool:
        try:
            return self._execute_command(["--version"])[0]
        except:
            return False

    def execute(self) -> SpeedTestResult:
        if not self._is_cli_available():
            raise CLINotInstalledException("LibreSpeed-CLI", "LibreSpeedSpeedTest", "execute")

        start: float = time.perf_counter()
        result: tuple[bool, str, str] = self._execute_command(["--json"])
        end: float = time.perf_counter()
        time_needed: float = end - start

        speedtest_result: Any = json.loads(result[1])
        client: Any = speedtest_result["client"]
        server: Any = speedtest_result["server"]

        return SpeedTestResult(
            0,
            datetime.now().isoformat(),
            result[0],
            speedtest_result["download"],
            speedtest_result["upload"],
            speedtest_result["ping"],
            speedtest_result["jitter"],
            server["name"],
            None,
            None,
            server["url"],
            None,
            client["ip"],
            result[2],
            time_needed,
            SpeedTestTool.LIBRESPEED_CLI,
        )
