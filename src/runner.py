import time
from network_checker import NetworkChecker
from datetime import datetime
from app_logger import AppLogger
from database_manager import DatabaseManager
from exceptions import CustomException, ObjectIsNotPreparedException, ThreadIsAlreadyRunningException
from outage_detector import OutageDetector
from app_settings_manager import AppSettingsManager
from threading import Lock, Thread, Event
from models import (
    LatencyTestResult,
    LatencyTestGroupResult,
    LogType,
    OutageDetectorResult,
    OutageChangeState,
)


class Runner:
    _lock_thread: Lock = Lock()
    _lock_is_prepared: Lock = Lock()

    _database_manager: DatabaseManager
    _settings_manager: AppSettingsManager
    _is_prepared: bool = False
    _latency_test_group_thread: Thread | None = None
    _stop_event: Event = Event()

    @classmethod
    def _check_running_unlocked(cls, method_name: str) -> None:
        if cls._latency_test_group_thread is not None and cls._latency_test_group_thread.is_alive():
            raise ThreadIsAlreadyRunningException("Runner", "Runner", LogType.SYSTEM, "Runner", method_name, True)

    @classmethod
    def _check_prepared(cls, method_name: str) -> None:
        with cls._lock_is_prepared:
            if not cls._is_prepared:
                raise ObjectIsNotPreparedException(
                    "Runner",
                    "Runner",
                    LogType.SYSTEM,
                    "Runner",
                    method_name,
                    True,
                )

    @classmethod
    def _run_latency_tests(cls, targets: list[str], network_checker: NetworkChecker) -> LatencyTestGroupResult:
        cls._check_prepared("_run_latency_tests")

        AppLogger.extended_debug(
            LogType.SCAN,
            "Starting latency group test",
            "Runner",
            "_run_latency_tests",
            details={"targets": targets},
        )

        start: float = time.perf_counter()
        start_time: str = datetime.now().isoformat()
        test_results: list[LatencyTestResult] = []

        if len(targets) == 0:
            raise CustomException(
                "No targets configured",
                LogType.SCAN,
                "Runner",
                "_run_latency_tests",
            )

        success_list: list[bool] = []

        for target in targets:
            test_result: LatencyTestResult = network_checker.test_latency(target)
            test_results.append(test_result)
            success_list.append(test_result.success)

        any_success: bool = any(success_list)
        group_success: bool = (len(success_list) > 0) and all(success_list)
        end_time: str = datetime.now().isoformat()

        end: float = time.perf_counter()
        time_needed_sec: float = end - start

        AppLogger.extended_debug(
            LogType.SCAN,
            "Ended latency group test",
            "Runner",
            "_run_latency_tests",
            details={
                "targets": targets,
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

    @classmethod
    def _run_latency_test_group(cls) -> None:
        try:
            cls._check_prepared("_run_latency_test_group")

            max_failed_group_test_count: int = (
                cls._settings_manager.get_app_settings().get_latency_test_settings().get_max_failed_group_test_count()
            )

            network_checker = NetworkChecker()
            outage_detector = OutageDetector(max_failed_group_test_count)

            while not cls._stop_event.is_set():
                targets: list[str] = cls._settings_manager.get_app_settings().get_latency_test_settings().get_targets()
                interval_seconds: int = (
                    cls._settings_manager.get_app_settings().get_latency_test_settings().get_interval_seconds()
                )

                if interval_seconds < 1:
                    AppLogger.warning(
                        LogType.SYSTEM,
                        "Interval for latency tests (in sec.) must be higher or equal to 1",
                        "Runner",
                        "_run_latency_test_group",
                    )
                    interval_seconds = 1

                outage_detector.update_max_failed_group_test_count(
                    cls._settings_manager.get_app_settings()
                    .get_latency_test_settings()
                    .get_max_failed_group_test_count()
                )

                latency_test_group_result: LatencyTestGroupResult = cls._run_latency_tests(targets, network_checker)

                if cls._stop_event.is_set():
                    return

                group_id: int = cls._database_manager.save_latency_test_group_result(latency_test_group_result)

                if cls._stop_event.is_set():
                    return

                detector_result: OutageDetectorResult = outage_detector.process_group_result(
                    latency_test_group_result, group_id
                )

                if detector_result.outage_change_state == OutageChangeState.STARTED.value:
                    AppLogger.info(
                        LogType.OUTAGE,
                        "Outage started",
                        "Runner",
                        "_run_latency_test_group",
                    )

                if detector_result.outage_change_state == OutageChangeState.ENDED.value:
                    outage_detection_result_id: int = cls._database_manager.save_outage(detector_result)
                    AppLogger.info(
                        LogType.OUTAGE,
                        "Outage ended",
                        "Runner",
                        "_run_latency_test_group",
                        related_object_type="OutageDetectorResult",
                        related_object_id=outage_detection_result_id,
                    )

                AppLogger.debug(
                    LogType.SYSTEM,
                    detector_result.connection_state,
                    "Runner",
                    "_run_latency_test_group",
                )

                if cls._stop_event.is_set():
                    return

                cls._stop_event.wait(interval_seconds)
        except CustomException:
            cls._stop_event.set()
        except Exception as ex:
            AppLogger.error(LogType.SYSTEM, str(ex), "Runner", "_run_latency_test_group")
            cls._stop_event.set()

    @classmethod
    def prepare(cls, database_manager: DatabaseManager, settings_manager: AppSettingsManager) -> None:
        with cls._lock_thread:
            cls._check_running_unlocked("prepare")
        cls._settings_manager = settings_manager
        cls._database_manager = database_manager

        AppLogger.info(LogType.SYSTEM, "Runner prepared", "Runner", "prepare")

        with cls._lock_is_prepared:
            cls._is_prepared = True

    @classmethod
    def run(cls) -> None:
        try:
            cls._check_prepared("run")

            AppLogger.info(LogType.SYSTEM, "Runner starting threads", "Runner", "run")

            with cls._lock_thread:
                cls._check_running_unlocked("run")
                cls._stop_event.clear()
                cls._latency_test_group_thread = Thread(target=cls._run_latency_test_group)
                cls._latency_test_group_thread.start()
            AppLogger.info(LogType.SYSTEM, "Latency test group thread started", "Runner", "run")

        except CustomException:
            cls._stop_event.set()

            if cls._latency_test_group_thread is not None and cls._latency_test_group_thread.is_alive():
                cls._latency_test_group_thread.join()

        except Exception as ex:
            cls._stop_event.set()

            if cls._latency_test_group_thread is not None and cls._latency_test_group_thread.is_alive():
                cls._latency_test_group_thread.join()

            AppLogger.error(LogType.SYSTEM, str(ex), "Runner", "run")

    @classmethod
    def stop(cls) -> None:
        AppLogger.info(LogType.SYSTEM, "Runner stop requested", "Runner", "stop")

        cls._stop_event.set()

        if cls._latency_test_group_thread is not None and cls._latency_test_group_thread.is_alive():
            cls._latency_test_group_thread.join()

        AppLogger.info(LogType.SYSTEM, "Runner stopped", "Runner", "stop")

    @classmethod
    def is_running(cls) -> bool:
        with cls._lock_thread:
            return cls._latency_test_group_thread is not None and cls._latency_test_group_thread.is_alive()
