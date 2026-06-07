from threading import Lock
import json
from typing import Any


class LatencyTestSettings:
    def __init__(self) -> None:
        self._lock_targets: Lock = Lock()
        self._lock_interval_seconds: Lock = Lock()
        self._lock_max_failed_group_test_count: Lock = Lock()

        self._targets: list[str] = ["1.1.1.1"]
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

    def _add_settings(self, settings_name: str, settings_json: str) -> None:
        settings: dict[str, Any] = json.loads(settings_json)
        match settings_name:
            case "latency_test_settings_targets":
                self.get_latency_test_settings().set_targets(settings["targets"])
            case "latency_test_settings_interval_seconds":
                self.get_latency_test_settings().set_interval_seconds(settings["interval"])
            case "latency_test_settings_max_failed_group_test_count":
                self.get_latency_test_settings().set_max_failed_group_test_count(settings["count"])
            case _:
                pass

    def add_from_dict(self, dict: list[tuple[str, str]]) -> None:
        for settings_name, settings_json in dict:
            self._add_settings(settings_name, settings_json)

    def add_from_tuple(self, tuple: tuple[str, str]) -> None:
        self._add_settings(tuple[0], tuple[1])

    def add_from_strings(self, settings_name: str, settings_json: str) -> None:
        self._add_settings(settings_name, settings_json)

    def get_as_dict(self) -> list[tuple[str, object]]:
        return [
            (
                "latency_test_settings_targets",
                {"targets": self.get_latency_test_settings().get_targets()},
            ),
            (
                "latency_test_settings_interval_seconds",
                {"interval": self.get_latency_test_settings().get_interval_seconds()},
            ),
            (
                "latency_test_settings_max_failed_group_test_count",
                {"count": self.get_latency_test_settings().get_max_failed_group_test_count()},
            ),
        ]

    def get_latency_test_settings(self) -> LatencyTestSettings:
        with self._lock_latency_test_settings:
            return self._latency_test_settings
