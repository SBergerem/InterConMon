from network_checker import NetworkChecker
from datetime import datetime
import time
from models import LatencyTestResult, LatencyTestGroupResult, LogType
from app_logger import AppLogger
from database_manager import DatabaseManager
from exceptions import ObjectIsNoneException


class Runner:
    _database_manager: DatabaseManager | None = None
    _network_checker: NetworkChecker | None = None
    _targets: list[str] | None = None

    @classmethod
    def _run_latency_tests(cls) -> LatencyTestGroupResult:
        try:
            AppLogger.extended_debug(
                LogType.SCAN,
                "Starting latency tests",
                "Runner",
                "_run_latency_tests",
                details={"targets": cls._targets},
            )

            start: float = time.perf_counter()

            start_time: str = datetime.now().isoformat()
            end_time: str | None = None
            time_needed_sec: float = -1.0
            any_success: bool = False
            group_success: bool = False
            test_results: list[LatencyTestResult] = []

            if cls._targets is None or cls._targets.count == 0:
                AppLogger.warning(
                    LogType.SCAN,
                    "No targets configured",
                    "Runner",
                    "_run_latency_tests",
                )
                raise ObjectIsNoneException(
                    "No targets configured",
                    LogType.SCAN,
                    "Runner",
                    "_run_latency_tests",
                )

            if cls._network_checker is None:
                raise ObjectIsNoneException(
                    "Network checker is None",
                    LogType.SCAN,
                    "Runner",
                    "_run_latency_tests",
                )

            success_list: list[bool] = []

            for target in cls._targets:
                test_result: LatencyTestResult = cls._network_checker.test_latency(
                    target
                )
                test_results.append(test_result)
                success_list.append(test_result.success)

            any_success = any(success_list)
            group_success = (len(success_list) > 0) and all(success_list)
            end_time = datetime.now().isoformat()

            end: float = time.perf_counter()
            time_needed_sec = end - start

            AppLogger.extended_debug(
                LogType.SCAN,
                "Ended latency tests",
                "Runner",
                "_run_latency_tests",
                details={
                    "targets": cls._targets,
                    "any_success": any_success,
                    "group_success": group_success,
                    "time_needed_sec": time_needed_sec,
                },
            )

            return LatencyTestGroupResult(
                start_time=start_time,
                end_time=end_time,
                time_needed_sec=time_needed_sec,
                any_success=any_success,
                group_success=group_success,
                test_results=test_results,
            )
        except Exception as ex:
            raise ex

    @classmethod
    def prepare(cls, database_manager: DatabaseManager, targets: list[str]) -> None:
        cls._targets = targets
        cls._database_manager = database_manager
        cls._network_checker = NetworkChecker()
        AppLogger.info(LogType.SYSTEM, "Runner prepared", "Runner", "prepare")

    @classmethod
    def run(cls) -> LatencyTestGroupResult | None:
        AppLogger.info(LogType.SYSTEM, "Runner started", "Runner", "run")

        while True:
            try:
                latency_test_group_result: LatencyTestGroupResult = (
                    cls._run_latency_tests()
                )
                group_id: int = cls._database_manager.save_latency_test_group_result(
                    latency_test_group_result
                )
                detector_result: OutageDetectorResult = (
                    outage_detector.process_group_result(test_group, group_id)
                )

                if (
                    detector_result.outage_change_state
                    == OutageChangeState.STARTED.value
                ):
                    AppLogger.info(LogType.SYSTEM, "Outage started", "main", "main")
                if detector_result.outage_change_state == OutageChangeState.ENDED.value:
                    outage_detection_result_id: int = database_manager.save_outage(
                        detector_result
                    )
                    AppLogger.info(
                        LogType.SYSTEM,
                        "Outage ended",
                        "main",
                        "main",
                        related_object_type="OutageDetectorResult",
                        related_object_id=outage_detection_result_id,
                    )

                AppLogger.debug(
                    LogType.SYSTEM, detector_result.connection_state, "main", "main"
                )
                time.sleep(1)
            except Exception:
                pass  # Exceptions are logging by themselfes
