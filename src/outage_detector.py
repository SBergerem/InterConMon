from datetime import datetime
from models import (
    OutageDetectorResult,
    ConnectionState,
    OutageChangeState,
    LatencyTestGroupResult,
    LogType,
)
from app_logger import AppLogger


class OutageDetector:

    def __init__(self) -> None:
        self._current_connection_state: ConnectionState = ConnectionState.UNKNOWN
        self._first_failed_test_time: str | None = None
        self._failed_groups_test_count = 0
        self._started_test_group_id: int | None = None
        self._max_failed_group_test_count: int = 3

    def process_group_result(self, group_result: LatencyTestGroupResult, group_id: int) -> OutageDetectorResult:
        AppLogger.extended_debug(
            LogType.OUTAGE,
            "Started outage check",
            "OutageDetector",
            "process_group_result",
            related_object_type="LatencyTestGroupResult",
            related_object_id=group_id,
        )

        test_succeeded: bool = group_result.any_success
        last_connection_state: ConnectionState = self._current_connection_state
        connection_test_date_time: str = group_result.end_time
        change_state: OutageChangeState = OutageChangeState.NONE
        start_time: str | None = None
        end_time: str = ""
        duration_sec: float = -1
        started_group_id: int | None = None
        ended_group_id: int | None = None

        if test_succeeded:
            if last_connection_state == ConnectionState.OFFLINE:
                change_state = OutageChangeState.ENDED
                start_time = self._first_failed_test_time
                end_time = connection_test_date_time

                if start_time is not None and end_time:
                    duration_sec = (
                        datetime.fromisoformat(end_time) - datetime.fromisoformat(start_time)
                    ).total_seconds()
                ended_group_id = group_id
                started_group_id = self._started_test_group_id

            self._current_connection_state = ConnectionState.ONLINE
            self._first_failed_test_time = None
            self._failed_groups_test_count = 0
            self._started_test_group_id = None
        else:
            if self._first_failed_test_time is None:
                self._first_failed_test_time = group_result.start_time

            if self._started_test_group_id is None:
                self._started_test_group_id = group_id
            started_group_id = self._started_test_group_id

            self._failed_groups_test_count += 1

            if self._failed_groups_test_count >= self._max_failed_group_test_count:
                start_time = self._first_failed_test_time

                if last_connection_state != ConnectionState.OFFLINE:
                    self._current_connection_state = ConnectionState.OFFLINE
                    change_state = OutageChangeState.STARTED

        AppLogger.extended_debug(
            LogType.OUTAGE,
            "Ended outage check",
            "OutageDetector",
            "process_group_result",
            related_object_type="LatencyTestGroupResult",
            related_object_id=group_id,
        )

        return OutageDetectorResult(
            0,
            self._current_connection_state.value,
            connection_test_date_time,
            change_state.value,
            start_time,
            end_time,
            duration_sec,
            started_group_id,
            ended_group_id,
        )

    def set_max_failed_group_test_count(self, max_failed_group_test_count: int) -> None:
        if max_failed_group_test_count < 1:
            AppLogger.warning(
                LogType.SYSTEM,
                "Can't update max_failed_group_test_count because the value is lower than 1.",
                "OutageDetector",
                "update_max_failed_group_test_count",
            )
        else:
            self._max_failed_group_test_count = max_failed_group_test_count
