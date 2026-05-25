import paho.mqtt.client as mqtt
import json
import time


class LightSimulator:
    def __init__(
        self,
        broker: str = "broker.emqx.io",
        port: int = 1883,
        prefix: str = "stanislawrayzacher_lightmanager",
    ):
        self.broker = broker
        self.port = port
        self.prefix = prefix
        self.client_id = "LightManager-Sim"

        if hasattr(mqtt, "CallbackAPIVersion"):
            self.client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2, client_id=self.client_id
            )
        else:
            self.client = mqtt.Client(client_id=self.client_id)

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def _get_time(self) -> str:
        return time.strftime("%X")

    def _on_connect(self, client, userdata, flags, rc, *args, **kwargs):
        print(f"[{self._get_time()}] Symulator połączony. Status podłączenia: {rc}")
        client.subscribe(f"{self.prefix}/registry/request")
        client.subscribe(f"{self.prefix}/device/+/command")
        print(f"[{self._get_time()}] Subskrypcje aktywne. Czekamy...")

    def _on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()

        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            return

        if topic.endswith("registry/request"):
            self._handle_registry_request(data)
        elif "/command" in topic:
            self._handle_command(topic, data)

    def _handle_registry_request(self, data: dict):
        uuid_str = data.get("uuid")
        name = data.get("name")
        print(f"\n=====================================")
        print(f"[{self._get_time()}] Nowy włącznik domaga się wejścia!")
        print(f"    UUID:  {uuid_str}")
        print(f"    NAZWA: {name}")

        # Opoznienie 0.3 sekundy aby uwiarygodnic fizyczne przypisanie
        time.sleep(0.3)
        self.client.publish(
            f"{self.prefix}/registry/confirm/{uuid_str}", json.dumps({"status": "ok"})
        )
        print(f"[{self._get_time()}] [OK] Odesłałem potwierdzenie instalacji sprzętu.")
        print(f"=====================================\n")

    def _handle_command(self, topic: str, data: dict):
        parts = topic.split("/")
        if len(parts) >= 2:
            uuid_str = parts[-2]
            command = data.get("command")
            print(f"\n[{self._get_time()}] ---> ODEBRANO KOMENDĘ <--")
            if command == "ON":
                print(
                    f"[UUID: {uuid_str}]  💡💡💡 KLIK: ŚWIATŁO ZOSTAŁO WŁĄCZONE 💡💡💡"
                )
            elif command == "OFF":
                print(f"[UUID: {uuid_str}]  🌑🌑🌑 KLIK: ŚWIATŁO ZGASŁO 🌑🌑🌑")
            print(f"----------------------------------------")

    def run(self):
        print(f"[{self._get_time()}] Symulator włączników oświetlenia w gotowości!")
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_forever()
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            print(f"Błąd uruchomienia: {e}")

    def stop(self):
        print(f"\n[{self._get_time()}] Wyłączanie symulatora.")
        self.client.disconnect()


if __name__ == "__main__":
    simulator = LightSimulator()
    simulator.run()
