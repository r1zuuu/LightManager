import uuid
import datetime
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from .db import engine, Base, get_db
from . import models, schemas
from .mqtt_client import mqtt_manager

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Startowanie połączenia z MQTT...")
    await mqtt_manager.start()
    yield
    print("Zamykanie z połączenia z MQTT...")
    await mqtt_manager.stop()

app = FastAPI(title="LightManager API - Sterownik i Statystyki", lifespan=lifespan)

@app.post("/switches/", response_model=schemas.SwitchResponse, status_code=201)
async def create_switch(switch_in: schemas.SwitchCreate, db: Session = Depends(get_db)):
    new_uuid = str(uuid.uuid4())
    
    # KROK 1: Asynchronicznie wysyłamy na MQTT żądanie i czekamy na odpowiedź
    print(f"Trwa dodawanie symulatora włącznika {new_uuid} / {switch_in.name}...")
    success = await mqtt_manager.request_registration(new_uuid, switch_in.name)
    
    if not success:
        raise HTTPException(
            status_code=504, 
            detail="Timeout (5s). Symulator urządzenia nie zareagował na próbę komunikacji."
        )
        
    # KROK 2: Dopisujemy poprawnie skonfigurowany włącznik do Bazy
    new_switch = models.Switch(id=new_uuid, name=switch_in.name)
    db.add(new_switch)
    db.commit()
    db.refresh(new_switch)
    print(f"Dodano do bazy: {new_switch.id}")
    
    return new_switch

@app.get("/switches/", response_model=list[schemas.SwitchResponse])
def get_switches(db: Session = Depends(get_db)):
    return db.query(models.Switch).all()

@app.patch("/switches/{switch_id}/state", response_model=schemas.SwitchResponse)
async def update_switch_state(switch_id: str, state_in: schemas.SwitchUpdate, db: Session = Depends(get_db)):
    db_switch = db.query(models.Switch).filter(models.Switch.id == switch_id).first()
    if not db_switch:
        raise HTTPException(status_code=404, detail="Nie odnaleziono sprzętu.")
        
    if db_switch.is_on and not state_in.is_on:
        # Zostało wyłączone, inkrementujemy czas świecenia
        if db_switch.last_turned_on:
            delta = (datetime.datetime.utcnow() - db_switch.last_turned_on).total_seconds()
            db_switch.total_time_seconds += delta
        db_switch.last_turned_on = None
        
    elif not db_switch.is_on and state_in.is_on:
        # Zostało włączone, start licznika
        db_switch.last_turned_on = datetime.datetime.utcnow()
        
    db_switch.is_on = state_in.is_on
    db.commit()
    db.refresh(db_switch)
    
    # Opublikuj decyzję dla symulatora
    command_str = "ON" if state_in.is_on else "OFF"
    await mqtt_manager.publish(f"device/{switch_id}/command", {"command": command_str})
    
    return db_switch
