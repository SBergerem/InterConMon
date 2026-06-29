from models.models import LatencyTest
from api.schemas.latency_test_schema import LatencyTestResponse, LatencyTestListResponse


class LatencyTestMapper:

    @classmethod
    def map_latency_test_to_response(cls, latency_test: LatencyTest | None) -> LatencyTestResponse | None:
        if latency_test is None:
            return None
        else:
            return LatencyTestResponse(
                id=latency_test.id,
                group_id=latency_test.group_id,
                date_time=latency_test.date_time,
                target=latency_test.target,
                test_target_type=latency_test.test_target_type.value,
                success=latency_test.success,
                latency_ms=latency_test.latency_ms,
                error_message=latency_test.error_message,
            )

    @classmethod
    def map_latency_tests_to_response(cls, latency_tests: list[LatencyTest] | None) -> LatencyTestListResponse:
        if latency_tests is None or len(latency_tests) == 0:
            return LatencyTestListResponse(items=None)
        else:
            responses: list[LatencyTestResponse | None] = []
            for entry in latency_tests:
                responses.append(cls.map_latency_test_to_response(entry))

            return LatencyTestListResponse(items=responses)
