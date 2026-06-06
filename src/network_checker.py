import platform
import subprocess
import os
import re
from datetime import datetime
from typing import Any, Literal
from ping3 import ping  # type: ignore[import]
from models import LatencyTestResult, LogType
from app_logger import AppLogger


class NetworkChecker:

    @classmethod
    def test_latency(cls, target: str) -> LatencyTestResult:
        AppLogger.detailed_debug(
            LogType.SCAN,
            "Starting ping test",
            "NetworkChecker",
            "test_latency",
            details={"target": target},
        )

        result = LatencyTestResult(
            date_time=datetime.now().isoformat(),
            target=target,
            success=False,
            latency_ms=None,
            error_message=None,
        )

        try:
            system: str = platform.system()

            if system == "Windows":
                latency: None | Any | Literal[False] = ping(target, unit="ms")

                if isinstance(latency, (int, float)) and not isinstance(latency, bool):
                    result.success = True
                    result.latency_ms = latency
                else:
                    result.success = False
                    result.error_message = f"Error: Ping failed or timed out! Target: {target}"
                    AppLogger.error(
                        LogType.SCAN,
                        result.error_message,
                        "NetworkChecker",
                        "test_latency",
                        details={"target": target, "ping_result": latency},
                    )

            elif system in ["Linux", "Darwin"]:
                env = os.environ.copy()
                env["LC_ALL"] = "C"
                env["LANG"] = "C"
                ping_result = subprocess.run(
                    ["ping", "-c", "1", target],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    encoding="utf-8",
                    errors="replace",
                    env=env,
                )

                if ping_result.returncode == 0:
                    latency_text: re.Match[str] | None = re.search(
                        r"time=\s*([0-9]+(?:\.[0-9]+)?)\s*ms", ping_result.stdout
                    )

                    result.success = True

                    if latency_text is not None:
                        result.latency_ms = float(latency_text.group(1))
                    else:
                        result.latency_ms = None
                        result.error_message = "Ping succeeded, but latency could not be parsed"
                        AppLogger.warning(
                            LogType.SCAN,
                            result.error_message,
                            "NetworkChecker",
                            "test_latency",
                            details={"target": target, "stdout": ping_result.stdout},
                        )
                else:
                    result.success = False
                    result.error_message = ping_result.stderr or ping_result.stdout or "Error: Ping failed or timed out"

                    AppLogger.error(
                        LogType.SCAN,
                        result.error_message,
                        "NetworkChecker",
                        "test_latency",
                        details={
                            "target": target,
                            "returncode": ping_result.returncode,
                        },
                    )
            else:
                result.success = False
                result.error_message = "Error: Can't ping. OS unknown"
                AppLogger.error(
                    LogType.SCAN,
                    result.error_message,
                    "NetworkChecker",
                    "test_latency",
                    details={"target": target},
                )

            if result.latency_ms is not None:
                latency_to_log: str = f"{result.latency_ms:.2f} ms"
            else:
                latency_to_log: str = "N/A"

            AppLogger.detailed_debug(
                LogType.SCAN,
                f"Ended latency test (Target: {target} | Latency: {latency_to_log})",
                "NetworkChecker",
                "test_latency",
                details={
                    "target": target,
                    "success": result.success,
                    "latency_ms": result.latency_ms,
                    "error_message": result.error_message,
                },
            )

        except Exception as ex:
            result.success = False
            result.error_message = str(ex)
            AppLogger.error(
                LogType.SCAN,
                result.error_message,
                "NetworkChecker",
                "test_latency",
                details={"target": target},
            )

        return result
