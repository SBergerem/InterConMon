from models.models import LatencyTest, LatencyTestGroup
from database.latency_test_repository import LatencyTestRepository
from database.latency_test_group_repository import LatencyTestGroupRepository
from api.schemas.latency_test_schema import LatencyTestListResponse
from api.mappers.latency_test_mapper import LatencyTestMapper


class LatencyTestService:

    def __init__(self, latency_test_repository: LatencyTestRepository, latency_test_group_repository: LatencyTestGroupRepository) -> None:
        self._latency_test_repository: LatencyTestRepository = latency_test_repository
        self._latency_test_group_repository: LatencyTestGroupRepository = latency_test_group_repository

    def get_latest_latency_groups(self, limit: int) -> LatencyTestListResponse:
        result: list[LatencyTestGroup] = self._latency_test_group_repository.load_latest_list(limit)
        
        
        return LatencyTestMapper.map_latency_tests_to_response(result)
