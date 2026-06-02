from network_checker import NetworkChecker
from datetime import datetime
import time
from models import LatencyTestResult, LatencyTestGroupResult

class Runner:
    _network_checker = None

    @classmethod
    def _run_latency_tests(cls, targets):
        if cls._network_checker is None:
            cls._network_checker = NetworkChecker()
        
        group_result = LatencyTestGroupResult(
            start_time=None,
            end_time=None,
            time_needed_sec=None,
            any_success=None,
            group_success=None,
            test_results=[],
        )

        start = time.perf_counter()

        group_result.start_time = datetime.now().isoformat()

        success_list = []

        for target in targets:
            test_result = cls._network_checker.test_latency(target)

            group_result.test_results.append(
                LatencyTestResult(
                    date_time=test_result.date_time,
                    target=target,
                    success=test_result.success,
                    latency_ms=test_result.latency_ms,
                    error_message=test_result.error_message,
                )
            )

            success_list.append(test_result.success)

        group_result.any_success = any(success_list)
        group_result.group_success = (len(success_list) > 0) and all(success_list)
        group_result.end_time = datetime.now().isoformat()

        end = time.perf_counter()
        duration_secs = end - start
        group_result.time_needed_sec = duration_secs

        return group_result

    @classmethod
    def run_tests(cls):
        targets = ["1.1.1.1"]  # later from config-table in mysql
        return cls._run_latency_tests(targets)
