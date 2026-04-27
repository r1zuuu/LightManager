import asyncio
import aiomqtt
import json
import logging

logger = logging.getLogger(__name__)

BROKER = "broker.emqx.io"
PORT = 1883
PREFIX = "stanislawrayzacher_lightmanager"

class MQTTManager:
    def __init__(self):
        self.client = None
        self.pending_confirmations = {}
        self.task = None

    async def connect_and_listen(self):
        while True:
            try:
                async with aiomqtt.Client(BROKER, PORT) as client:
                    self.client = client
                    logger.info("Webapp connected to MQTT broker.")
                    await client.subscribe(f"{PREFIX}/registry/confirm/+")
                    
                    async for message in client.messages:
                        topic = str(message.topic)
                        payload = message.payload.decode()
                        logger.info(f"Otrzymano po MQTT: {topic} -> {payload}")
                        
                        if "/registry/confirm/" in topic:
                            uuid_str = topic.split("/")[-1]
                            if uuid_str in self.pending_confirmations:
                                future = self.pending_confirmations[uuid_str]
                                if not future.done():
                                    future.set_result(True)
                                    
            except Exception as e:
                logger.error(f"MQTT Error: {e}. Reconnecting in 3 seconds...")
                await asyncio.sleep(3)

    async def start(self):
        self.task = asyncio.create_task(self.connect_and_listen())

    async def stop(self):
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            
    async def publish(self, topic_suffix: str, payload: dict):
        if self.client:
            await self.client.publish(f"{PREFIX}/{topic_suffix}", payload=json.dumps(payload))
            return True
        return False

    async def request_registration(self, uuid_str: str, name: str) -> bool:
        future = asyncio.Future()
        self.pending_confirmations[uuid_str] = future
        
        await self.publish("registry/request", {"uuid": uuid_str, "name": name})
        
        try:
            # Opóźnienie / timeout - aplikacja czeka do 5s na symulator
            await asyncio.wait_for(future, timeout=5.0)
            return True
        except asyncio.TimeoutError:
            return False
        finally:
            self.pending_confirmations.pop(uuid_str, None)

mqtt_manager = MQTTManager()
