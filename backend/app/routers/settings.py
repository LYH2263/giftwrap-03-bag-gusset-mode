from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.repositories import settings_repo
router = APIRouter()


class BagGussetBody(BaseModel):
    bag_gusset: float


@router.get("/settings")
def settings(): return settings_repo.get_all()


@router.put("/settings/bag-gusset")
def update_bag_gusset(body: BagGussetBody):
    try:
        v = settings_repo.set_bag_gusset(body.bag_gusset)
    except ValueError as e:
        raise HTTPException(422, str(e))
    return {"bag_gusset": v}
