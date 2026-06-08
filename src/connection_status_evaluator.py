from models import LatencyTestGroup, Outage, ConnectionDiagnosis, ConnectionState, ReachabilityState
from datetime import datetime


class ConnectionStatusEvaluator:

    @classmethod
    def create_diagnosis(cls, latency_test_group: LatencyTestGroup, outage: Outage) -> ConnectionDiagnosis:
        connection_state: ConnectionState = ConnectionState.UNKNOWN

        if latency_test_group.any_success and (outage.reachibility_state == ReachabilityState.REACHABLE):
            connection_state = ConnectionState.INTERNET_CONNECTION
        elif latency_test_group.any_success and (outage.reachibility_state != ReachabilityState.REACHABLE):
            connection_state = ConnectionState.NO_INTERNET_CONNECTION
        elif not latency_test_group.any_success and (outage.reachibility_state != ReachabilityState.REACHABLE):
            connection_state = ConnectionState.NO_GATEWAY_CONNECTION
        else:
            connection_state = ConnectionState.INTERNAL_NETWORK_ERROR

        return ConnectionDiagnosis(
            0, datetime.now().isoformat(), connection_state, latency_test_group.id, latency_test_group, outage.id, outage
        )
