from api.schemas.connection_diagnosis_schema import ConnectionDiagnosisResponse, LatestConnectionDiagnosisResponse
from models.models import ConnectionDiagnosis


class ConnectionDiagnosisMapper:

    @classmethod
    def map_connection_diagnosis_response(cls, connection_diagnosis: ConnectionDiagnosis | None) -> LatestConnectionDiagnosisResponse:
        if connection_diagnosis is None:
            return LatestConnectionDiagnosisResponse(item=None)
        else:
            return LatestConnectionDiagnosisResponse(
                item=ConnectionDiagnosisResponse(
                    id=connection_diagnosis.id,
                    date_time=connection_diagnosis.date_time,
                    network_diagnosis_type=connection_diagnosis.network_diagnosis_type,
                    gateway_latency_test_group_id=connection_diagnosis.gateway_latency_test_group_id,
                    server_latency_test_group_id=connection_diagnosis.server_latency_test_group_id,
                )
            )
