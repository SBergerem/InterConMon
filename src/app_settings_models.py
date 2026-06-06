from threading import Lock


class LatencyTestSettings:
    def __init__(self) -> None:
        self._lock_targets: Lock = Lock()
        self._lock_interval_seconds: Lock = Lock()
        self._lock_max_failed_group_test_count: Lock = Lock()

        self._targets: list[str] = []
        self._interval_seconds: int = 1
        self._max_failed_group_test_count: int = 3

    def get_targets(self) -> list[str]:
        with self._lock_targets:
            return self._targets.copy()

    def get_interval_seconds(self) -> int:
        with self._lock_interval_seconds:
            return self._interval_seconds

    def get_max_failed_group_test_count(self) -> int:
        with self._lock_max_failed_group_test_count:
            return self._max_failed_group_test_count

    def set_targets(self, targets: list[str]) -> None:
        with self._lock_targets:
            self._targets = targets

    def set_interval_seconds(self, interval_seconds: int) -> None:
        with self._lock_interval_seconds:
            self._interval_seconds = interval_seconds

    def set_max_failed_group_test_count(self, max_failed_group_test_count: int) -> None:
        with self._lock_max_failed_group_test_count:
            self._max_failed_group_test_count = max_failed_group_test_count


class AppSettings:

    def __init__(self) -> None:
        self._lock_latency_test_settings: Lock = Lock()

        self._latency_test_settings: LatencyTestSettings = LatencyTestSettings()

    def get_latency_test_settings(self) -> LatencyTestSettings:
        with self._lock_latency_test_settings:
            return self._latency_test_settings
