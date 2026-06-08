from threading import Lock
import json
from typing import Any
from exceptions import ValueInvalidException


class LatencyTestSettings:

    def __init__(self) -> None:
        self._lock_targets: Lock = Lock()
        self._lock_interval_seconds: Lock = Lock()
        self._lock_enabled: Lock = Lock()

        self._targets: list[str] = ["1.1.1.1"]
        self._interval_seconds: int = 1
        self._enabled: bool = False

    def get_targets(self) -> list[str]:
        with self._lock_targets:
            return self._targets.copy()

    def get_interval_seconds(self) -> int:
        with self._lock_interval_seconds:
            return self._interval_seconds

    def get_enabled(self) -> bool:
        with self._lock_enabled:
            return self._enabled

    def set_targets(self, targets: list[str]) -> None:
        if len(targets) == 0:
            raise ValueInvalidException("LatencyTestSettings", "set_targets", len(targets), "Length of targets is 0")

        with self._lock_targets:
            self._targets = targets

    def set_interval_seconds(self, interval_seconds: int) -> None:
        if interval_seconds < 1.0:
            raise ValueInvalidException("LatencyTestSettings", "set_interval_seconds", interval_seconds, "Value is lower than 1.0")

        with self._lock_interval_seconds:
            self._interval_seconds = interval_seconds

    def set_enabled(self, enabled: bool) -> None:
        with self._lock_enabled:
            self._enabled = enabled


class OutageCheckSettings:

    def __init__(self) -> None:
        self._lock_max_failed_group_test_count: Lock = Lock()
        self._lock_enabled: Lock = Lock()

        self._max_failed_group_test_count: int = 3
        self._enabled: bool = False

    def get_max_failed_group_test_count(self) -> int:
        with self._lock_max_failed_group_test_count:
            return self._max_failed_group_test_count

    def get_enabled(self) -> bool:
        with self._lock_enabled:
            return self._enabled

    def set_max_failed_group_test_count(self, max_failed_group_test_count: int) -> None:
        if max_failed_group_test_count < 1:
            raise ValueInvalidException(
                "OutageSettings", "set_max_failed_group_test_count", max_failed_group_test_count, "Value is lower than 1"
            )

        with self._lock_max_failed_group_test_count:
            self._max_failed_group_test_count = max_failed_group_test_count

    def set_enabled(self, enabled: bool) -> None:
        with self._lock_enabled:
            self._enabled = enabled


class GatewayTestSettings:

    def __init__(self) -> None:
        self._lock_targets: Lock = Lock()
        self._lock_enabled: Lock = Lock()
        self._lock_interval_seconds: Lock = Lock()

        self._targets: list[str] = []
        self._enabled: bool = False
        self._interval_seconds: int = 1

    def get_targets(self) -> list[str]:
        with self._lock_targets:
            return self._targets

    def get_enabled(self) -> bool:
        with self._lock_enabled:
            return self._enabled

    def get_interval_seconds(self) -> int:
        with self._lock_interval_seconds:
            return self._interval_seconds

    def set_targets(self, targets: list[str]) -> None:
        with self._lock_targets:
            self._targets = targets

    def set_enabled(self, enabled: bool) -> None:
        with self._lock_enabled:
            self._enabled = enabled

    def set_interval_seconds(self, interval: int) -> None:
        if interval < 1:
            raise ValueInvalidException("GatewayTestSettings", "set_interval_seconds", interval, "Value is lower than 1.0")

        with self._lock_interval_seconds:
            self._interval_seconds = interval


class AppSettings:

    def __init__(self) -> None:
        self._lock_latency_test_settings: Lock = Lock()
        self._lock_gateway_test_settings: Lock = Lock()
        self._lock_outage_check_settings: Lock = Lock()

        self._latency_test_settings: LatencyTestSettings = LatencyTestSettings()
        self._gateway_test_settings: GatewayTestSettings = GatewayTestSettings()
        self._outage_check_settings: OutageCheckSettings = OutageCheckSettings()

    def _add_settings(self, settings_name: str, settings_json: str) -> None:
        settings: dict[str, Any] = json.loads(settings_json)
        match settings_name:
            case "latency_test_settings.targets":
                self.get_latency_test_settings().set_targets(settings["targets"])
            case "latency_test_settings.interval_seconds":
                self.get_latency_test_settings().set_interval_seconds(settings["interval"])
            case "latency_test_settings.enabled":
                self.get_latency_test_settings().set_enabled(settings["enabled"])
            case "outage_check.enabled":
                self.get_outage_check_settings().set_enabled(settings["enabled"])
            case "outage_check.max_failed_group_test_count":
                self.get_outage_check_settings().set_max_failed_group_test_count(settings["count"])
            case "gateway_test.enabled":
                self.get_gateway_test_settings().set_enabled(settings["enabled"])
            case "gateway_test.targets":
                self.get_gateway_test_settings().set_targets(settings["targets"])
            case "gateway_test.interval_seconds":
                self.get_gateway_test_settings().set_interval_seconds(settings["interval"])
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
                "latency_test_settings.enabled",
                {"enabled": self.get_latency_test_settings().get_enabled()},
            ),
            (
                "latency_test_settings.targets",
                {"targets": self.get_latency_test_settings().get_targets()},
            ),
            (
                "latency_test_settings.interval_seconds",
                {"interval": self.get_latency_test_settings().get_interval_seconds()},
            ),
            (
                "outage_check.enabled",
                {"enabled": self.get_outage_check_settings().get_enabled()},
            ),
            (
                "outage_check.max_failed_group_test_count",
                {"count": self.get_outage_check_settings().get_max_failed_group_test_count()},
            ),
            (
                "gateway_test.targets",
                {"targets": self.get_gateway_test_settings().get_targets()},
            ),
            (
                "gateway_test.enabled",
                {"enabled": self.get_gateway_test_settings().get_enabled()},
            ),
            (
                "gateway_test.interval_seconds",
                {"interval": self.get_gateway_test_settings().get_interval_seconds()},
            ),
        ]

    def get_latency_test_settings(self) -> LatencyTestSettings:
        with self._lock_latency_test_settings:
            return self._latency_test_settings

    def get_gateway_test_settings(self) -> GatewayTestSettings:
        with self._lock_gateway_test_settings:
            return self._gateway_test_settings

    def get_outage_check_settings(self) -> OutageCheckSettings:
        with self._lock_outage_check_settings:
            return self._outage_check_settings
