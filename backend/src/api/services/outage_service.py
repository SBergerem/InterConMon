from database.outage_repository import OutageRepository
from api.mappers.outage_mapper import OutageMapper
from api.schemas.outage_schema import OutageListResponse
from models.models import Outage


class OutageService:

    def __init__(self, repository: OutageRepository) -> None:
        self._repository: OutageRepository = repository

    def get_latest_outages(self, limit: int) -> OutageListResponse:
        outages: list[Outage] | None = self._repository.load_latest_list(limit)
        return OutageMapper.map_outages_to_response(outages)
