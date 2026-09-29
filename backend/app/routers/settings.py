from fastapi import APIRouter, HTTPException
from app.schemas.estimate import SettingsUpdate
from app.repositories import settings_repo
router = APIRouter()
@router.get("/settings")
def settings(): return settings_repo.get_all()
@router.put("/settings")
def update_settings(body: SettingsUpdate):
    if body.overlap is not None:
        if body.overlap <= 0:
            raise HTTPException(422, "overlap must be positive")
        settings_repo.set_value("overlap", str(float(body.overlap)))
    if body.gusset_m is not None:
        if body.gusset_m <= 0:
            raise HTTPException(422, "default gusset_m must be positive")
        settings_repo.set_value("gusset_m", str(float(body.gusset_m)))
    return settings_repo.get_all()
