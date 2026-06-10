from models import LatencyTestGroup, Outage, ConnectionDiagnosis, NetworkDiagnosisType, ReachabilityState
from datetime import datetime


class ConnectionStatusEvaluator:

    @classmethod
    def create_diagnosis(cls, latency_test_group: LatencyTestGroup, outage: Outage) -> ConnectionDiagnosis:
        network_diagnosis_type: NetworkDiagnosisType = NetworkDiagnosisType.UNKNOWN

        if latency_test_group.any_success and (outage.reachibility_state == ReachabilityState.REACHABLE):
            network_diagnosis_type = NetworkDiagnosisType.INTERNET_CONNECTION
        elif latency_test_group.any_success and (outage.reachibility_state != ReachabilityState.REACHABLE):
            network_diagnosis_type = NetworkDiagnosisType.NO_INTERNET_CONNECTION
        elif not latency_test_group.any_success and (outage.reachibility_state != ReachabilityState.REACHABLE):
            network_diagnosis_type = NetworkDiagnosisType.NO_GATEWAY_CONNECTION
        else:
            network_diagnosis_type = NetworkDiagnosisType.INTERNAL_NETWORK_ERROR

        return ConnectionDiagnosis(
            0, datetime.now().isoformat(), network_diagnosis_type, latency_test_group.id, latency_test_group, outage.id, outage
        )
