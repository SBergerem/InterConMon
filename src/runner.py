import time
from network_checker import NetworkChecker
from datetime import datetime
from app_logger import AppLogger
from database.database_manager import DatabaseManager
from exceptions import CustomException, ThreadStoppedException
from outage_detector import OutageDetector
from threading import Thread, Event
from models import LatencyTestResult, LatencyTestGroupResult, LogType, OutageDetectorResult, OutageChangeState, ConnectionState
from app_settings import AppSettings, LatencyTestSettings
from database.latency_test_group_repository import LatencyTestGroupRepository
from database.latency_test_repository import LatencyTestRepository
from database.outage_repository import OutageRepository
from sqlite3 import Cursor


class Runner:

    def __init__(self, database_manager: DatabaseManager, app_settings: AppSettings) -> None:
        self._loop_thread: Thread | None = None
        self._stop_event: Event = Event()
        self._app_settings: AppSettings = app_settings
        self._database_manager: DatabaseManager = database_manager
        self._latency_test_repository: LatencyTestRepository = LatencyTestRepository(database_manager)
        self._latency_test_group_repository: LatencyTestGroupRepository = LatencyTestGroupRepository(database_manager)
        self._outage_repository: OutageRepository = OutageRepository(database_manager)

    # Main loop of the runner
    def _loop(self) -> None:
        try:
            outage_detector = OutageDetector()
            network_checker = NetworkChecker()
            latency_test_settings: LatencyTestSettings = self._app_settings.get_latency_test_settings()

            next_latency_test: float = 0.0

            while not self._stop_event.is_set():
                if next_latency_test < time.time():
                    latency_result: LatencyTestGroupResult = self._run_latency_tests(network_checker, latency_test_settings.get_targets())

                    if self._stop_event.is_set():
                        raise ThreadStoppedException("Runner", "_loop", "self._loop_thread")

                    max_failed_count: int = latency_test_settings.get_max_failed_group_test_count()
                    self._run_outage_detection(outage_detector, max_failed_count, latency_result)
                    next_latency_test = time.time() + latency_test_settings.get_interval_seconds()

                self._stop_event.wait(0.1)

            raise ThreadStoppedException("Runner", "_loop", "self._loop_thread")  # Because it can only end, when the stop was requested.
        except ThreadStoppedException as ex:
            AppLogger.info(LogType.SYSTEM, str(ex), ex.class_name, ex.function_name)
        except CustomException as ex:
            AppLogger.error(LogType.SCAN, str(ex), ex.class_name, ex.function_name)
            self._stop_event.set()
        except Exception as ex:
            AppLogger.error(LogType.SCAN, str(ex), "Runner", "_loop")
            self._stop_event.set()

    # Runs all the latency tests and returns the result of these tests
    def _run_latency_test_group(self, targets: list[str], network_checker: NetworkChecker) -> LatencyTestGroupResult:
        AppLogger.extended_debug(
            LogType.SCAN,
            "Starting latency group test",
            "Runner",
            "_run_latency_test_group",
            details={"targets": targets},
        )

        start: float = time.perf_counter()
        start_time: str = datetime.now().isoformat()
        test_results: list[LatencyTestResult] = []

        if len(targets) == 0:
            raise CustomException(
                "Runner",
                "_run_latency_test_group",
                "No targets configured",
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

        details: dict[str, object] = {
            "targets": targets,
            "any_success": any_success,
            "group_success": group_success,
            "time_needed_sec": time_needed_sec,
        }

        AppLogger.extended_debug(LogType.SCAN, "Ended latency group test", "Runner", "_run_latency_test_group", details=details)

        return LatencyTestGroupResult(
            0,
            start_time,
            end_time,
            time_needed_sec,
            any_success,
            group_success,
            test_results,
        )

    # Save the group and the single results in a transaction. So that if something wrent wrong, neither the group nor the single tests get saved
    def _save_latency_test_results(
        self, cursor: Cursor, latency_test_results: list[LatencyTestResult], latency_test_group_result: LatencyTestGroupResult
    ) -> None:
        self._latency_test_group_repository.save_in_transaction([latency_test_group_result], cursor)
        self._latency_test_repository.save_in_transaction(latency_test_results, cursor)

    # Collects the test result and the group_id, so we can give it the outage detector
    def _run_latency_tests(self, network_checker: NetworkChecker, targets: list[str]) -> LatencyTestGroupResult:
        result: LatencyTestGroupResult = self._run_latency_test_group(targets, network_checker)
        self._database_manager.run_in_transaction(lambda cursor: self._save_latency_test_results(cursor, result.test_results, result))
        return result

    # Checks for an outage and logs it
    def _run_outage_detection(
        self,
        outage_detector: OutageDetector,
        max_failed_group_test_count: int,
        latency_test_group_result: LatencyTestGroupResult,
    ) -> bool:
        outage_detector.set_max_failed_group_test_count(max_failed_group_test_count)

        detector_result: OutageDetectorResult = outage_detector.process_group_result(latency_test_group_result)

        if detector_result.change_state == OutageChangeState.STARTED.value:
            AppLogger.info(LogType.OUTAGE, "Outage started", "Runner", "_run_outage_detection")

        if detector_result.change_state == OutageChangeState.ENDED.value:
            self._outage_repository.save([detector_result])
            AppLogger.info(
                LogType.OUTAGE,
                "Outage ended",
                "Runner",
                "_run_outage_detection",
                related_object_type="OutageDetectorResult",
                related_object_id=detector_result.id,
            )

        AppLogger.debug(LogType.SYSTEM, detector_result.connection_state, "Runner", "_run_outage_detection")

        return detector_result.connection_state == ConnectionState.ONLINE.value

    # Checks, if the thread isn't already running. If it's not it's starting the thread
    def run(self) -> None:
        try:
            if self.is_running():
                AppLogger.warning(LogType.SYSTEM, "Runner already started", "Runner", "run")
                return

            AppLogger.info(LogType.SYSTEM, "Runner starting thread", "Runner", "run")
            self._stop_event.clear()
            self._loop_thread = Thread(target=self._loop)
            self._loop_thread.start()
            AppLogger.info(LogType.SYSTEM, "Runner thread started", "Runner", "run")
        except Exception as ex:
            self._stop_event.set()

            if self.is_running():
                self._loop_thread.join()  # type: ignore

            AppLogger.error(LogType.SYSTEM, str(ex), "Runner", "run")

    # Stop request send to the thread and waiting for it to stop
    def stop(self) -> None:
        AppLogger.info(LogType.SYSTEM, "Runner stop requested", "Runner", "stop")

        self._stop_event.set()

        if self.is_running():
            self._loop_thread.join()  # type: ignore

        AppLogger.info(LogType.SYSTEM, "Runner stopped", "Runner", "stop")

    # Return True, if the thread is already running. Checks log
    def is_running(self) -> bool:
        return self._loop_thread is not None and self._loop_thread.is_alive()
