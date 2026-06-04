from dataclasses import dataclass, field

@dataclass
class LatencyTestSettings:
    targets: list[str] = field(default_factory=lambda: list[str]())
    interval_seconds: int = 3

@dataclass
class AppSettings:
    latency_test_settings: LatencyTestSettings = field(
        default_factory=LatencyTestSettings
    )