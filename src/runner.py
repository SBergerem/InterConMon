import time
from network_checker import NetworkChecker
from app_logger import AppLogger
from exceptions import CustomException, ThreadStoppedException
from outage_detector import OutageDetector
from threading import Thread, Event
from models import (
    LatencyTest,
    LatencyTestGroup,
    LogType,
    Outage,
    OutageChangeState,
    SpeedTestResult,
    TestTargetType,
    ConnectionDiagnosis,
    NetworkDiagnosisType,
)
from app_settings import AppSettings, LatencyTestSettings, GatewayTestSettings, OutageCheckSettings, SpeedTestSettings
from database.database_manager import DatabaseManager
from database.latency_test_group_repository import LatencyTestGroupRepository
from database.latency_test_repository import LatencyTestRepository
from database.outage_repository import OutageRepository
from database.connection_diagnosis_repository import ConnectionDiagnosisRepository
from database.speed_test_result_repository import SpeedTestResultRepository
from sqlite3 import Cursor
from connection_diagnosis_evaluator import ConnectionDiagnosisEvaluator
from speedtest_executor import SpeedTestExecutor


class Runner:

    def __init__(self, database_manager: DatabaseManager, app_settings: AppSettings) -> None:
        self._loop_thread: Thread | None = None
        self._stop_event: Event = Event()
        self._app_settings: AppSettings = app_settings
        self._database_manager: DatabaseManager = database_manager
        self._latency_test_repository: LatencyTestRepository = LatencyTestRepository(database_manager)
        self._latency_test_group_repository: LatencyTestGroupRepository = LatencyTestGroupRepository(database_manager)
        self._outage_repository: OutageRepository = OutageRepository(database_manager)
        self._connection_diagnosis_repository: ConnectionDiagnosisRepository = ConnectionDiagnosisRepository(database_manager)
        self._speed_test_result_repository: SpeedTestResultRepository = SpeedTestResultRepository(database_manager)

    # Return True, if the thread is already running. Checks log
    def is_running(self) -> bool:
        return self._loop_thread is not None and self._loop_thread.is_alive()

    # Main loop of the runner
    def _loop(self) -> None:
        try:
            server_test_settings: LatencyTestSettings = self._app_settings.get_latency_test_settings()
            outage_check_settings: OutageCheckSettings = self._app_settings.get_outage_check_settings()
            gateway_test_settings: GatewayTestSettings = self._app_settings.get_gateway_test_settings()
            speed_test_settings: SpeedTestSettings = self._app_settings.get_speed_test_settings()

            latency_tests_outage_detector = OutageDetector()
            gateway_tests_outage_detector = OutageDetector()

            next_server_test: float = 0.0
            next_gateway_test: float = 0.0
            next_speed_test: float = 0.0
            next_nothing_to_do: float = 0.0

            server_test_group: LatencyTestGroup | None = None
            gateway_test_group: LatencyTestGroup | None = None

            was_last_connection_ok: bool = False

            while not self._stop_event.is_set():
                try:
                    if next_gateway_test < time.time():
                        next_gateway_test, gateway_test_group = self._run_latency_test_and_outage_check(
                            gateway_tests_outage_detector,
                            gateway_test_settings.get_targets(),
                            gateway_test_settings.get_enabled(),
                            outage_check_settings.get_enabled(),
                            outage_check_settings.get_max_failed_group_test_count(),
                            gateway_test_settings.get_interval_seconds(),
                            TestTargetType.GATEWAY,
                        )

                    if next_server_test < time.time():
                        next_server_test, server_test_group = self._run_latency_test_and_outage_check(
                            latency_tests_outage_detector,
                            server_test_settings.get_targets(),
                            server_test_settings.get_enabled(),
                            outage_check_settings.get_enabled(),
                            outage_check_settings.get_max_failed_group_test_count(),
                            server_test_settings.get_interval_seconds(),
                            TestTargetType.SERVER,
                        )

                    if gateway_test_group is not None and server_test_group is not None:
                        was_last_connection_ok = self._run_connection_diagnosis_evaluation(gateway_test_group, server_test_group)
                        gateway_test_group = None
                        server_test_group = None

                    if next_speed_test < time.time():
                        next_speed_test = self._run_speedtest(speed_test_settings, was_last_connection_ok)

                    if (
                        next_nothing_to_do < time.time()
                        and not gateway_test_settings.get_enabled()
                        and not server_test_settings.get_enabled()
                        and not outage_check_settings.get_enabled()
                        and not speed_test_settings.get_enabled()
                    ):
                        AppLogger.warning(LogType.SYSTEM, "Nothing to do. Everything is disabled..", "Runner", "_loop")
                        next_nothing_to_do = time.time() + 2

                    self._stop_event.wait(0.1)
                except CustomException as ex:
                    AppLogger.error(LogType.SCAN, str(ex), ex.class_name, ex.function_name)
                    self._stop_event.set()
                except Exception as ex:
                    AppLogger.error(LogType.SCAN, str(ex), "Runner", "_loop")
                    self._stop_event.set()
                    raise

            raise ThreadStoppedException("Runner", "_loop", "self._loop_thread")  # Because it can only end, when the stop was requested.
        except ThreadStoppedException as ex:
            AppLogger.info(LogType.SYSTEM, str(ex), ex.class_name, ex.function_name)

    def _run_latency_test_and_outage_check(
        self,
        outage_detector: OutageDetector,
        targets: list[str],
        latency_test_enabled: bool,
        outage_check_enabled: bool,
        max_failed_group_test_count: int,
        interval_seconds: int,
        test_target_type: TestTargetType,
    ) -> tuple[float, LatencyTestGroup | None]:
        next_check: float = time.time() + interval_seconds

        if not latency_test_enabled:
            return (next_check, None)

        test_group: LatencyTestGroup = NetworkChecker.run_test_group(targets, test_target_type)
        self._database_manager.run_in_transaction(lambda cursor: self._save_latency_tests(cursor, test_group.tests, test_group))

        if self._stop_event.is_set():
            raise ThreadStoppedException("Runner", "_run_latency_test_and_outage_check", "self._loop_thread")

        if outage_check_enabled:
            outage: Outage = self._run_outage_detection(outage_detector, max_failed_group_test_count, test_group, test_target_type)

            if outage.change_state == OutageChangeState.ENDED:
                self._outage_repository.save([outage])
                AppLogger.info(
                    LogType.OUTAGE,
                    "Outage ended",
                    "Runner",
                    "_run_outage_detection",
                    related_object_type="Outage",
                    related_object_id=outage.id,
                )

        return (next_check, test_group)

    # Save the group and the single tests in a transaction. So that if something wrent wrong, neither the group nor the single tests get saved
    def _save_latency_tests(self, cursor: Cursor, latency_tests: list[LatencyTest], latency_test_group: LatencyTestGroup) -> None:
        self._latency_test_group_repository.save_in_transaction([latency_test_group], cursor)
        self._latency_test_repository.save_in_transaction(latency_tests, cursor)

    # Checks for an outage and logs it
    def _run_outage_detection(
        self,
        outage_detector: OutageDetector,
        max_failed_group_test_count: int,
        latency_test_group: LatencyTestGroup,
        test_target_type: TestTargetType,
    ) -> Outage:
        outage_detector.set_max_failed_group_test_count(max_failed_group_test_count)

        outage: Outage = outage_detector.check_group(latency_test_group, test_target_type)

        if outage.change_state == OutageChangeState.STARTED:
            AppLogger.info(LogType.OUTAGE, "Outage started", "Runner", "_run_outage_detection")

        AppLogger.debug(LogType.SYSTEM, f"{test_target_type} {outage.reachability_state}", "Runner", "_run_outage_detection")

        return outage

    # runs and saves connection diagnosis
    def _run_connection_diagnosis_evaluation(self, gateway_test_group: LatencyTestGroup, server_test_group: LatencyTestGroup) -> bool:
        connection_diagnosis: ConnectionDiagnosis = ConnectionDiagnosisEvaluator.create_diagnosis(gateway_test_group, server_test_group)
        self._connection_diagnosis_repository.save([connection_diagnosis])
        return connection_diagnosis.network_diagnosis_type == NetworkDiagnosisType.EXTERNAL_CONNECTION

    def _run_speedtest(self, speed_test_settings: SpeedTestSettings, is_connected_ok: bool) -> float:
        next_speed_test: float = (speed_test_settings.get_interval_minutes() * 60) + time.time()

        try:
            if not speed_test_settings.get_enabled():
                return next_speed_test

            only_when_connection_ok: bool = speed_test_settings.get_only_when_connection_ok()

            if only_when_connection_ok and not is_connected_ok:
                return next_speed_test

            speed_test_result: SpeedTestResult = SpeedTestExecutor(speed_test_settings).run()
            self._speed_test_result_repository.save([speed_test_result])
        except CustomException as ex:
            AppLogger.error(LogType.SYSTEM, str(ex), ex.class_name, ex.function_name)

        return next_speed_test

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
