from fastapi import FastAPI
from backend.src.api.api_context import ApiContext
from backend.src.api.routes.health_routes import router as health_router
from backend.src.api.routes.speed_test_routes import router as speedtests_router
from backend.src.api.routes.connection_routes import router as connection_router
from backend.src.api.routes.logs_routes import router as log_router
from backend.src.api.routes.outages_routes import router as outage_router


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

    return app
