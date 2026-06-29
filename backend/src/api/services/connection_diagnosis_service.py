from database.connection_diagnosis_repository import ConnectionDiagnosisRepository
from api.mappers.connection_diagnosis_mapper import ConnectionDiagnosisMapper
from api.schemas.connection_diagnosis_schema import LatestConnectionDiagnosisResponse
from models.models import ConnectionDiagnosis


class ConnectionDiagnosisService:

    def __init__(self, repository: ConnectionDiagnosisRepository) -> None:
        self._repository: ConnectionDiagnosisRepository = repository

    def get_latest_connection_diagnosis(self) -> LatestConnectionDiagnosisResponse:
        connection_diagnosis: ConnectionDiagnosis | None = self._repository.load_latest()
        return ConnectionDiagnosisMapper.map_connection_diagnosis_response(connection_diagnosis)
