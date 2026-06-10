import platform
import subprocess
import os
import re
from datetime import datetime
from typing import Any, Literal
from ping3 import ping  # type: ignore[import]
from models import LatencyTest, LatencyTestGroup, LogType, TestTargetType
from app_logger import AppLogger
from exceptions import ListIsEmptyException
import time


class NetworkChecker:

    @classmethod
    def test_latency(cls, target: str, test_target_type: TestTargetType) -> LatencyTest:
        AppLogger.detailed_debug(
            LogType.SCAN,
            "Starting ping test",
            "NetworkChecker",
            "test_latency",
            details={"target": target},
        )

        success: bool = False
        latency_ms: float | None = None
        error_message: str = ""
        date_time: str = datetime.now().isoformat()

        try:
            system: str = platform.system()

            if system == "Windows":
                latency: None | Any | Literal[False] = ping(target, unit="ms")

                if isinstance(latency, (int, float)) and not isinstance(latency, bool):
                    success = True
                    latency_ms = latency
                else:
                    success = False
                    error_message = f"Error: Ping failed or timed out! Target: {target}"
                    AppLogger.error(
                        LogType.SCAN,
                        error_message,
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
                    latency_text: re.Match[str] | None = re.search(r"time=\s*([0-9]+(?:\.[0-9]+)?)\s*ms", ping_result.stdout)

                    success = True

                    if latency_text is not None:
                        latency_ms = float(latency_text.group(1))
                    else:
                        latency_ms = None
                        error_message = "Ping succeeded, but latency could not be parsed"
                        AppLogger.warning(
                            LogType.SCAN,
                            error_message,
                            "NetworkChecker",
                            "test_latency",
                            details={"target": target, "stdout": ping_result.stdout},
                        )
                else:
                    success = False
                    error_message = ping_result.stderr or ping_result.stdout or "Error: Ping failed or timed out"

                    AppLogger.error(
                        LogType.SCAN,
                        error_message,
                        "NetworkChecker",
                        "test_latency",
                        details={
                            "target": target,
                            "returncode": ping_result.returncode,
                        },
                    )
            else:
                success = False
                error_message = "Error: Can't ping. OS unknown"
                AppLogger.error(
                    LogType.SCAN,
                    error_message,
                    "NetworkChecker",
                    "test_latency",
                    details={"target": target},
                )

            if latency_ms is not None:
                latency_to_log: str = f"{latency_ms:.2f} ms"
            else:
                latency_to_log: str = "N/A"

            AppLogger.detailed_debug(
                LogType.SCAN,
                f"Ended latency test (Target: {target} | Latency: {latency_to_log})",
                "NetworkChecker",
                "test_latency",
                details={
                    "target": target,
                    "success": success,
                    "latency_ms": latency_ms,
                    "error_message": error_message,
                },
            )

        except Exception as ex:
            success = False
            error_message = str(ex)
            AppLogger.error(
                LogType.SCAN,
                error_message,
                "NetworkChecker",
                "test_latency",
                details={"target": target},
            )

        return LatencyTest(0, 0, date_time, target, test_target_type, success, latency_ms, error_message)

    @classmethod
    def run_test_group(cls, targets: list[str], test_target_type: TestTargetType) -> LatencyTestGroup:
        if len(targets) == 0:
            raise ListIsEmptyException("NetworkChecker", "create_group", "latency_tests", "list[LatencyTest]")

        AppLogger.extended_debug(
            LogType.SCAN,
            "Starting latency group test",
            "Runner",
            "_run_latency_test_group",
            details={"targets": targets},
        )

        start: float = time.perf_counter()
        start_time: str = datetime.now().isoformat()
        tests: list[LatencyTest] = []

        success_list: list[bool] = []
        for target in targets:
            test: LatencyTest = cls.test_latency(target, test_target_type)
            tests.append(test)
            success_list.append(test.success)

        any_success: bool = any(success_list)
        group_success: bool = (len(success_list) > 0) and all(success_list)
        end_time: str = datetime.now().isoformat()

        end: float = time.perf_counter()
        time_needed_sec: float = end - start

        details: dict[str, object] = {
            "targets": targets,
            "any_success": any_success,
            "group_success": group_success,
            "time_needed_sec": time_needed_sec,
        }

        AppLogger.extended_debug(LogType.SCAN, "Ended latency group test", "Runner", "_run_latency_test_group", details=details)

        return LatencyTestGroup(
            0,
            start_time,
            end_time,
            time_needed_sec,
            any_success,
            group_success,
            test_target_type,
            tests,
        )
