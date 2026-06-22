from backend.src.models.models import LatencyTestGroup, ConnectionDiagnosis, NetworkDiagnosisType, LogType
from datetime import datetime
from backend.src.utils.app_logger import AppLogger


class ConnectionDiagnosisEvaluator:

    @classmethod
    def create_diagnosis(
        cls, gateway_latency_test_group: LatencyTestGroup, server_latency_test_group: LatencyTestGroup
    ) -> ConnectionDiagnosis:
        network_diagnosis_type: NetworkDiagnosisType = NetworkDiagnosisType.UNKNOWN

        is_gateway_connected: bool = gateway_latency_test_group.any_success
        is_server_connected: bool = server_latency_test_group.any_success

        if is_gateway_connected and is_server_connected:
            network_diagnosis_type = NetworkDiagnosisType.EXTERNAL_CONNECTION
        elif is_gateway_connected and not is_server_connected:
            network_diagnosis_type = NetworkDiagnosisType.NO_EXTERNAL_CONNECTION
        elif not is_gateway_connected and not is_server_connected:
            network_diagnosis_type = NetworkDiagnosisType.NO_GATEWAY_CONNECTION
        else:
            network_diagnosis_type = NetworkDiagnosisType.INTERNAL_NETWORK_ERROR

        AppLogger.detailed_debug(
            LogType.SCAN,
            "Diagnosis created",
            "ConnectionDiagnosisEvaluator",
            "create_diagnosis",
            details={"network_diagnosis_type": network_diagnosis_type.value},
        )

        return ConnectionDiagnosis(
            0,
            datetime.now().isoformat(),
            network_diagnosis_type,
            gateway_latency_test_group.id,
            gateway_latency_test_group,
            server_latency_test_group.id,
            server_latency_test_group,
        )
