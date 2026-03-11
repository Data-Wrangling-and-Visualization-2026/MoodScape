from fastapi import APIRouter, HTTPException

from backend.services.parse_service.api.admin_controller import usecase


router = APIRouter(prefix="/internal/v1", tags=["internal"])


@router.get("/tracks/{track_id}/payload")
def get_track_payload(track_id: str):
    """Return parsed payload for `llm_service` once track data is fully ready."""
    # Provide internal payload endpoint so llm_service can fetch metadata/lyrics/dsp
    # from parse_service without exposing extra admin/testing routes.
    payload = usecase.get_track_payload_for_llm(track_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Track not ready or not found")
    return payload
