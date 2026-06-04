from dataclasses import dataclass


@dataclass
class LatencyTestSettings:
    targets: list[str] = []
    interval_seconds: int = 3


@dataclass
class AppSettings:
    latency_test_settings: LatencyTestSettings = LatencyTestSettings()
