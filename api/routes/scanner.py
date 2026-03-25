from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from api.scanner.universes import UniverseNotFoundError
from api.schemas.scanner import ScanRequest, ScanResponse, UniverseOption
from api.services.scanner_service import scanner_service

router = APIRouter(prefix="/scanner", tags=["scanner"])


@router.get("/universes", response_model=list[UniverseOption])
def list_universes() -> list[UniverseOption]:
    return [UniverseOption(**item) for item in scanner_service.get_universes()]


@router.post("/run", response_model=ScanResponse)
def run_scan_endpoint(request: ScanRequest) -> ScanResponse:
    try:
        return ScanResponse(**scanner_service.run_scan(request.universe, request.mode))
    except UniverseNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/export")
def export_scan(request: ScanRequest) -> Response:
    try:
        content = scanner_service.export_csv(request.universe, request.mode)
    except UniverseNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    filename = f"scanner-results-{request.universe}-{request.mode}-{date.today().isoformat()}.csv"
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename=\"{filename}\"'},
    )
