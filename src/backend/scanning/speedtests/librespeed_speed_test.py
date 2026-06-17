from backend.scanning.speedtests.base_speed_test import BaseSpeedTest
from backend.models.models import SpeedTestResult, SpeedTestTool
from backend.exceptions.exceptions import CLINotInstalledException
from datetime import datetime
import json
from typing import Any
import time


class LibreSpeedSpeedTest(BaseSpeedTest):

    def _set_console_start_command(self) -> None:
        self._console_start_command = "librespeed-cli"

    def _create_error_result(self, error_message: str | None, time_needed: float) -> SpeedTestResult:
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
            error_message,
            time_needed,
            SpeedTestTool.LIBRESPEED_CLI,
        )

    def execute(self) -> SpeedTestResult:
        if not self._is_cli_available("librespeed-cli"):
            raise CLINotInstalledException("LibreSpeed-CLI", "LibreSpeedSpeedTest", "execute")

        start: float = time.perf_counter()
        result: tuple[bool, str, str] = self._execute_command(["--json"])
        end: float = time.perf_counter()
        time_needed: float = end - start

        error_message: str | None = result[2] if result[2] != "" else None

        if not result[0]:
            return self._create_error_result(error_message, time_needed)

        speedtest_result: Any = {}
        try:
            # index of 0, because librespeed-cli returns a list
            speedtest_result = json.loads(result[1])[0]
        except Exception:
            error_message = "Could not parse LibreSpeed JSON result"
            return self._create_error_result(error_message, time_needed)

        client: Any = speedtest_result.get("client") or {}
        server: Any = speedtest_result.get("server") or {}

        return SpeedTestResult(
            0,
            datetime.now().isoformat(),
            True,
            speedtest_result.get("download"),
            speedtest_result.get("upload"),
            speedtest_result.get("ping"),
            speedtest_result.get("jitter"),
            server.get("name") or None,
            None,
            None,
            server.get("url") or None,
            None,
            client.get("ip") or None,
            error_message,
            time_needed,
            SpeedTestTool.LIBRESPEED_CLI,
        )
