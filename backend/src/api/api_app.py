from fastapi import FastAPI
from api.api_context import ApiContext
from api.routes.health_routes import router as health_router
from api.routes.speed_test_routes import router as speedtests_router
from api.routes.connection_diagnosis_routes import router as connection_router
from api.routes.logs_routes import router as log_router
from api.routes.outages_routes import router as outage_router
from api.routes.settings_routes import router as settings_router


def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "app": "InterConMon",
    }


def create_app(api_context: ApiContext) -> FastAPI:
    app = FastAPI(title="InterConMon API")

    app.state.api_context = api_context

    app.include_router(health_router)
    app.include_router(speedtests_router)
    app.include_router(connection_router)
    app.include_router(log_router)
    app.include_router(outage_router)
    app.include_router(settings_router)

    return app
