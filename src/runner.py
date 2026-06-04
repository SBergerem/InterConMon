from network_checker import NetworkChecker
from datetime import datetime
import time
from models import LatencyTestResult, LatencyTestGroupResult, LogType
from app_logger import AppLogger


class Runner:
    _network_checker: NetworkChecker | None = None
    _targets: list[str] | None = None

    @classmethod
    def _run_latency_tests(cls) -> LatencyTestGroupResult | None:
        if cls._network_checker is None:
            cls._network_checker = NetworkChecker()

        AppLogger.extended_debug(
            LogType.SCAN,
            "Starting latency tests",
            "Runner",
            "_run_latency_tests",
            details={"targets": cls._targets},
        )

        start: float = time.perf_counter()

        group_result = LatencyTestGroupResult(
            start_time=datetime.now().isoformat(),
            end_time="",
            time_needed_sec=-1.0,
            any_success=False,
            group_success=False,
            test_results=[],
        )

        if cls._targets is None or cls._targets == []:
            AppLogger.warning(
                LogType.SCAN,
                "No targets configured",
                "Runner",
                "_run_latency_tests",
            )
            return None

        success_list: list[bool] = []

        for target in cls._targets:
            test_result: LatencyTestResult = cls._network_checker.test_latency(target)
            group_result.test_results.append(test_result)
            success_list.append(test_result.success)

        group_result.any_success = any(success_list)
        group_result.group_success = (len(success_list) > 0) and all(success_list)
        group_result.end_time = datetime.now().isoformat()

        end: float = time.perf_counter()
        duration_secs: float = end - start
        group_result.time_needed_sec = duration_secs

        AppLogger.extended_debug(
            LogType.SCAN,
            "Ended latency tests",
            "Runner",
            "_run_latency_tests",
            details={
                "targets": cls._targets,
                "any_success": group_result.any_success,
                "group_success": group_result.group_success,
                "time_needed_sec": group_result.time_needed_sec,
            },
        )

        return group_result

    @classmethod
    def prepare(cls, targets: list[str]) -> None:
        cls._targets = targets

    @classmethod
    def run_tests(cls) -> LatencyTestGroupResult | None:
        return cls._run_latency_tests()
