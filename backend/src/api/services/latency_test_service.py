from models.models import LatencyTest
from database.latency_test_repository import LatencyTestRepository
from api.schemas.latency_test_schema import LatencyTestListResponse
from api.mappers.latency_test_mapper import LatencyTestMapper


class LatencyTestService:

    def __init__(self, repository: LatencyTestRepository) -> None:
        self._repository: LatencyTestRepository = repository

    def get_latest_latencies(self, limit: int) -> LatencyTestListResponse:
        result: list[LatencyTest] = self._repository.load_latest_list(limit)
        return LatencyTestMapper.map_latency_tests_to_response(result)
