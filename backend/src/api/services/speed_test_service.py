from database.speed_test_result_repository import SpeedTestResultRepository
from api.mappers.speed_test_mapper import SpeedTestMapper
from api.schemas.speed_test_schema import SpeedTestListResponse
from models.models import SpeedTestResult


class SpeedTestService:

    def __init__(self, repository: SpeedTestResultRepository) -> None:
        self._repository: SpeedTestResultRepository = repository

    def get_latest_speed_tests(self, limit: int) -> SpeedTestListResponse:
        speed_tests: list[SpeedTestResult] | None = self._repository.load_latest_list(limit)
        return SpeedTestMapper.map_speed_tests_to_response(speed_tests)
