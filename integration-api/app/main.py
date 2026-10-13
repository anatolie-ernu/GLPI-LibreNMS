from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Response, status

from .config import get_settings
from .db import CorrelationStore
from .glpi import GLPIClient
from .librenms import LibreNMSClient
from .models import (
    AssetNetworkResponse,
    Correlation,
    EndpointResolution,
    EventAccepted,
    HealthResponse,
    LibreNmsEvent,
)
from .security import require_api_key, require_webhook_secret
from .service import IntegrationService

settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    errors = settings.validate_runtime()
    if errors:
        raise RuntimeError("; ".join(errors))

    store = CorrelationStore(settings.database_path)
    store.initialize()

    librenms = LibreNMSClient(
        settings.librenms_base_url,
        settings.librenms_api_token,
        verify_tls=settings.librenms_verify_tls,
    )
    glpi = GLPIClient(
        settings.glpi_base_url,
        settings.glpi_app_token,
        settings.glpi_user_token,
        verify_tls=settings.glpi_verify_tls,
        asset_itemtype=settings.glpi_asset_itemtype,
        default_group_id=settings.glpi_default_group_id,
    )
    app.state.librenms = librenms
    app.state.glpi = glpi
    app.state.service = IntegrationService(store, librenms, glpi)
    try:
        yield
    finally:
        await librenms.close()
        await glpi.close()


app = FastAPI(
    title="GLPI LibreNMS Integration API",
    version="0.2.0",
    description="Internal correlation and alert-to-ticket service.",
    lifespan=lifespan,
)


def service() -> IntegrationService:
    return app.state.service


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/ready", response_model=HealthResponse)
async def ready(response: Response) -> HealthResponse:
    librenms_ok, glpi_ok = await asyncio.gather(
        app.state.librenms.reachable(),
        app.state.glpi.reachable(),
    )
    ok = librenms_ok and glpi_ok
    if not ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthResponse(
        status="ok" if ok else "degraded",
        librenms="reachable" if librenms_ok else "unreachable",
        glpi="reachable" if glpi_ok else "unreachable",
    )


@app.get(
    "/v1/endpoints/by-ip/{ip}",
    response_model=EndpointResolution,
    dependencies=[Depends(require_api_key)],
)
async def endpoint_by_ip(ip: str, svc: IntegrationService = Depends(service)):
    try:
        result = await svc.endpoint_by_ip(ip)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not result:
        raise HTTPException(status_code=404, detail="endpoint not found")
    return result


@app.get(
    "/v1/endpoints/by-mac/{mac}",
    response_model=EndpointResolution,
    dependencies=[Depends(require_api_key)],
)
async def endpoint_by_mac(mac: str, svc: IntegrationService = Depends(service)):
    try:
        result = await svc.endpoint_by_mac(mac)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not result:
        raise HTTPException(status_code=404, detail="endpoint not found")
    return result


@app.get(
    "/v1/assets/{asset_id}/network",
    response_model=AssetNetworkResponse,
    dependencies=[Depends(require_api_key)],
)
async def asset_network(asset_id: int, svc: IntegrationService = Depends(service)):
    result = await svc.asset_network(asset_id)
    if not result:
        raise HTTPException(status_code=404, detail="asset/network evidence not found")
    return result


@app.post(
    "/v1/events/librenms",
    response_model=EventAccepted,
    status_code=202,
    dependencies=[Depends(require_webhook_secret)],
)
async def librenms_event(
    event: LibreNmsEvent, svc: IntegrationService = Depends(service)
):
    return await svc.handle_event(event)


@app.get(
    "/v1/correlations/{key:path}",
    response_model=Correlation,
    dependencies=[Depends(require_api_key)],
)
async def get_correlation(key: str, svc: IntegrationService = Depends(service)):
    result = svc.get_correlation(key)
    if not result:
        raise HTTPException(status_code=404, detail="correlation not found")
    return result
