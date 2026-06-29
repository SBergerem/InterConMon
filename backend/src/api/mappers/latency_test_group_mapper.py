from backend.src.api.schemas.latency_test_schema import LatencyTestListResponse, LatencyTestResponse
from models.models import LatencyTestGroup
from api.schemas.latency_test_group_schema import LatencyTestGroupResponse, LatencyTestGroupListResponse
from api.mappers.latency_test_mapper import LatencyTestMapper


class LatencyTestGroupMapper:

    @classmethod
    def map_latency_test_to_response(cls, latency_test_group: LatencyTestGroup | None) -> LatencyTestGroupResponse | None:
        if latency_test_group is None:
            return None
        else:
            tests: LatencyTestListResponse = LatencyTestMapper.map_latency_tests_to_response(latency_test_group.tests)
            if tests.items is None or len(tests.items) == 0:
                items = None
            else:
                items: list[LatencyTestResponse | None] | None = tests.items

            return LatencyTestGroupResponse(
                id=latency_test_group.id,
                start_time=latency_test_group.start_time,
                end_time=latency_test_group.end_time,
                time_needed_sec=latency_test_group.time_needed_sec,
                any_success=latency_test_group.any_success,
                group_success=latency_test_group.group_success,
                test_target_type=latency_test_group.test_target_type.value,
                tests=items,
            )

    @classmethod
    def map_latency_tests_to_response(cls, latency_test_groups: list[LatencyTestGroup] | None) -> LatencyTestGroupListResponse:
        if latency_test_groups is None or len(latency_test_groups) == 0:
            return LatencyTestGroupListResponse(items=None)
        else:
            responses: list[LatencyTestGroupResponse | None] = []
            for group in latency_test_groups:
                responses.append(cls.map_latency_test_to_response(group))

            return LatencyTestGroupListResponse(items=responses)
