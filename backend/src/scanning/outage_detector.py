from datetime import datetime
from backend.src.models.models import Outage, ReachabilityState, OutageChangeState, LatencyTestGroup, LogType, TestTargetType
from backend.src.utils.app_logger import AppLogger


class OutageDetector:

    def __init__(self) -> None:
        self._current_reachability_state: ReachabilityState = ReachabilityState.UNKNOWN
        self._first_failed_test_time: str | None = None
        self._failed_groups_test_count = 0
        self._started_test_group_id: int | None = None
        self._max_failed_group_test_count: int = 3

    def check_group(self, group: LatencyTestGroup, test_target_type: TestTargetType) -> Outage:
        AppLogger.extended_debug(
            LogType.OUTAGE,
            "Started outage check",
            "OutageDetector",
            "process_group",
            related_object_type="LatencyTestGroup",
            related_object_id=group.id,
        )

        test_succeeded: bool = group.any_success
        last_reachability_state: ReachabilityState = self._current_reachability_state
        connection_test_date_time: str = group.end_time
        change_state: OutageChangeState = OutageChangeState.NONE
        start_time: str | None = None
        end_time: str = ""
        duration_sec: float = -1
        started_group_id: int | None = None
        ended_group_id: int | None = None

        if test_succeeded:
            if last_reachability_state == ReachabilityState.UNREACHABLE:
                change_state = OutageChangeState.ENDED
                start_time = self._first_failed_test_time
                end_time = connection_test_date_time

                if start_time is not None and end_time:
                    duration_sec = (datetime.fromisoformat(end_time) - datetime.fromisoformat(start_time)).total_seconds()
                ended_group_id = group.id
                started_group_id = self._started_test_group_id

            self._current_reachability_state = ReachabilityState.REACHABLE
            self._first_failed_test_time = None
            self._failed_groups_test_count = 0
            self._started_test_group_id = None
        else:
            if self._first_failed_test_time is None:
                self._first_failed_test_time = group.start_time

            if self._started_test_group_id is None:
                self._started_test_group_id = group.id
            started_group_id = self._started_test_group_id

            self._failed_groups_test_count += 1

            if self._failed_groups_test_count >= self._max_failed_group_test_count:
                start_time = self._first_failed_test_time

                if last_reachability_state != ReachabilityState.UNREACHABLE:
                    self._current_reachability_state = ReachabilityState.UNREACHABLE
                    change_state = OutageChangeState.STARTED

        AppLogger.extended_debug(
            LogType.OUTAGE,
            "Ended outage check",
            "OutageDetector",
            "process_group",
            related_object_type="LatencyTestGroup",
            related_object_id=group.id,
        )

        return Outage(
            0,
            datetime.now().isoformat(),
            self._current_reachability_state,
            connection_test_date_time,
            change_state,
            test_target_type,
            start_time,
            end_time,
            duration_sec,
            started_group_id,
            None,
            ended_group_id,
            None,
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
