from network_checker import NetworkChecker
from datetime import datetime
import time
from models import LatencyTestResult, LatencyTestGroupResult, LogType
from app_logger import AppLogger


class Runner:
    _network_checker = None

    @classmethod
    def _run_latency_tests(cls, targets: list[str]) -> LatencyTestGroupResult:
        if cls._network_checker is None:
            cls._network_checker = NetworkChecker()

        AppLogger.extended_debug(
            LogType.SCAN,
            "Starting latency tests",
            "_run_latency_tests",
            details={"targets": targets},
        )

        start = time.perf_counter()

        group_result = LatencyTestGroupResult(
            start_time=datetime.now().isoformat(),
            end_time="",
            time_needed_sec=None,
            any_success=False,
            group_success=False,
            test_results=[],
        )

        success_list = []

        for target in targets:
            test_result = cls._network_checker.test_latency(target)
            group_result.test_results.append(test_result)
            success_list.append(test_result.success)

        group_result.any_success = any(success_list)
        group_result.group_success = (len(success_list) > 0) and all(success_list)
        group_result.end_time = datetime.now().isoformat()

        end = time.perf_counter()
        duration_secs = end - start
        group_result.time_needed_sec = duration_secs

        AppLogger.extended_debug(
            LogType.SCAN,
            "Ended latency tests",
            "_run_latency_tests",
            details={
                "targets": targets,
                "any_success": group_result.any_success,
                "group_success": group_result.group_success,
                "time_needed_sec": group_result.time_needed_sec,
            },
        )

        return group_result

    @classmethod
    def run_tests(cls) -> LatencyTestGroupResult:
        targets = ["1.1.1.1"]
        return cls._run_latency_tests(targets)
