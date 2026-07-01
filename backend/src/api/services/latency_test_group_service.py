from models.models import LatencyTestGroup
from database.latency_test_repository import LatencyTestRepository
from database.latency_test_group_repository import LatencyTestGroupRepository
from api.schemas.latency_test_group_schema import LatencyTestGroupListResponse
from api.mappers.latency_test_group_mapper import LatencyTestGroupMapper


class LatencyTestGroupService:

    def __init__(self, latency_test_repository: LatencyTestRepository, latency_test_group_repository: LatencyTestGroupRepository) -> None:
        self._latency_test_repository: LatencyTestRepository = latency_test_repository
        self._latency_test_group_repository: LatencyTestGroupRepository = latency_test_group_repository

    def get_latest_latency_groups(self, limit: int) -> LatencyTestGroupListResponse:
        result: list[LatencyTestGroup] = self._latency_test_group_repository.load_latest_list(limit)
        self._latency_test_repository.load_in_test_groups(result)
        return LatencyTestGroupMapper.map_latency_tests_to_response(result)
