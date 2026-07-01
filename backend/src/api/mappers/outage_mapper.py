from models.models import Outage
from api.schemas.outage_schema import OutageResponse, OutageListResponse


class OutageMapper:

    @classmethod
    def map_outage_to_response(cls, outage: Outage | None) -> OutageResponse | None:
        if outage is None:
            return None
        else:
            return OutageResponse(
                id=outage.id,
                date_time=outage.date_time,
                reachability_state=outage.reachability_state.value,
                last_connection_test=outage.last_connection_test,
                change_state=outage.change_state.value,
                test_target_type=outage.test_target_type.value,
                start_time=outage.start_time,
                end_time=outage.end_time,
                duration_sec=outage.duration_sec,
                started_group_id=outage.started_group_id,
                ended_group_id=outage.ended_group_id,
            )

    @classmethod
    def map_outages_to_response(cls, outages: list[Outage] | None) -> OutageListResponse:
        if outages is None or len(outages) == 0:
            return OutageListResponse(items=None)
        else:
            responses: list[OutageResponse | None] = []
            for outage in outages:
                responses.append(cls.map_outage_to_response(outage))

            return OutageListResponse(items=responses)
