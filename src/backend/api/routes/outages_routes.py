from fastapi import APIRouter, Request
from backend.api.api_context import ApiContext
from backend.database.outage_repository import OutageRepository
from backend.models.models import Outage
from typing import Any

router = APIRouter(prefix="/api/outages")


@router.get("/latest")
def get_latest(request: Request) -> dict[str, Any]:
    api_context: ApiContext = request.app.state.api_context

    repository: OutageRepository = api_context.outage_repository

    last_outage: Outage | None = repository.load_latest()

    if last_outage is None:
        return {"outage": None}

    return {
        "id": last_outage.id,
        "date_time": last_outage.date_time,
        "reachability_state": last_outage.reachability_state,
        "last_connection_test": last_outage.last_connection_test,
        "change_state": last_outage.change_state,
        "test_target_type": last_outage.test_target_type,
        "start_time": last_outage.start_time,
        "end_time": last_outage.end_time,
        "duration_sec": last_outage.duration_sec,
        "started_group_id": last_outage.started_group_id,
        "ended_group_id": last_outage.ended_group_id,
    }
