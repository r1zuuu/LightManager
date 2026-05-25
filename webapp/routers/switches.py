from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from webapp import schemas
from webapp.db import get_db
from webapp.services import switch_service

router = APIRouter(prefix="/switches", tags=["Switches"])


@router.post("/", response_model=schemas.SwitchResponse, status_code=201)
async def create_switch(switch_in: schemas.SwitchCreate, db: Session = Depends(get_db)):
    return await switch_service.create_switch(switch_in, db)


@router.get("/", response_model=list[schemas.SwitchResponse])
def get_switches(db: Session = Depends(get_db)):
    return switch_service.get_switches(db)


@router.patch("/{switch_id}/state", response_model=schemas.SwitchResponse)
async def update_switch_state(
    switch_id: str, state_in: schemas.SwitchUpdate, db: Session = Depends(get_db)
):
    return await switch_service.update_switch_state(switch_id, state_in, db)
