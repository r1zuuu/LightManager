import uuid
import datetime
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from .db import engine, Base, get_db
from . import models, schemas
from .mqtt_client import mqtt_manager
from webapp.routers import switches

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Startowanie połączenia z MQTT...")
    await mqtt_manager.start()
    yield
    print("Zamykanie z połączenia z MQTT...")
    await mqtt_manager.stop()


app = FastAPI(title="LightManager API - Sterownik i Statystyki", lifespan=lifespan)
app.include_router(switches.router)
