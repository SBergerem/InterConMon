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

    def __init__(self, max_failed_group_test_count: int) -> None:
        self._current_connection_state = ConnectionState.UNKNOWN
        self._first_failed_test_time: str | None = None
        self._failed_groups_test_count = 0
        self._outage_started_test_group_id: int | None = None

        if max_failed_group_test_count > 0:
            self._max_failed_group_test_count = max_failed_group_test_count
        else:
            self._max_failed_group_test_count = 1

    def process_group_result(
        self, group_result: LatencyTestGroupResult, group_id: int
    ) -> OutageDetectorResult:
        AppLogger.extended_debug(
            LogType.GENERAL,
            "Started process group result",
            "process_group_result",
            related_object_type="LatencyTestGroupResult",
            related_object_id=group_id,
        )

        test_succeeded = group_result.any_success
        last_connection_state = self._current_connection_state
        connection_test_date_time = group_result.end_time
        outage_change_state = OutageChangeState.NONE
        outage_start_time = None
        outage_end_time = None
        outage_duration_sec = None
        outage_started_group_id = None
        outage_ended_group_id = None

        if test_succeeded:
            if last_connection_state == ConnectionState.OFFLINE:
                outage_change_state = OutageChangeState.ENDED
                outage_start_time = self._first_failed_test_time
                outage_end_time = connection_test_date_time

                if outage_start_time is not None and outage_end_time is not None:
                    outage_duration_sec = (
                        datetime.fromisoformat(outage_end_time)
                        - datetime.fromisoformat(outage_start_time)
                    ).total_seconds()

                outage_ended_group_id = group_id
                outage_started_group_id = self._outage_started_test_group_id

            self._current_connection_state = ConnectionState.ONLINE
            self._first_failed_test_time = None
            self._failed_groups_test_count = 0
            self._outage_started_test_group_id = None
        else:
            if self._first_failed_test_time is None:
                self._first_failed_test_time = group_result.start_time

            if self._outage_started_test_group_id is None:
                self._outage_started_test_group_id = group_id
            outage_started_group_id = self._outage_started_test_group_id

            self._failed_groups_test_count += 1

            if self._failed_groups_test_count >= self._max_failed_group_test_count:
                outage_start_time = self._first_failed_test_time

                if last_connection_state != ConnectionState.OFFLINE:
                    self._current_connection_state = ConnectionState.OFFLINE
                    outage_change_state = OutageChangeState.STARTED

        AppLogger.extended_debug(
            LogType.GENERAL,
            "Ended process group result",
            "process_group_result",
            related_object_type="LatencyTestGroupResult",
            related_object_id=group_id,
        )

        return OutageDetectorResult(
            connection_state=self._current_connection_state.value,
            last_connection_test=connection_test_date_time,
            outage_change_state=outage_change_state.value,
            outage_start_time=outage_start_time,
            outage_end_time=outage_end_time,
            outage_duration_sec=outage_duration_sec,
            outage_started_group_id=outage_started_group_id,
            outage_ended_group_id=outage_ended_group_id,
        )
