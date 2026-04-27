import paho.mqtt.client as mqtt
import json
import time

BROKER = "test.mosquitto.org"
PORT = 1883
PREFIX = "stanislawrayzacher_lightmanager"

def on_connect(client, userdata, flags, rc, *args, **kwargs):
    print(f"[{time.strftime('%X')}] Symulator połączony. Status podłączenia: {rc}")
    client.subscribe(f"{PREFIX}/registry/request")
    client.subscribe(f"{PREFIX}/device/+/command")
    print(f"[{time.strftime('%X')}] Subskrypcje aktywne. Czekamy...")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return

    if topic.endswith("registry/request"):
        uuid_str = data.get("uuid")
        name = data.get("name")
        print(f"\n=====================================")
        print(f"[{time.strftime('%X')}] Nowy włącznik domaga się wejścia!")
        print(f"    UUID:  {uuid_str}")
        print(f"    NAZWA: {name}")
        
        # Opoznienie 0.3 sekundy aby uwiarygodnic fizyczne przypisanie
        time.sleep(0.3)
        client.publish(f"{PREFIX}/registry/confirm/{uuid_str}", json.dumps({"status": "ok"}))
        print(f"[{time.strftime('%X')}] [OK] Odesłałem potwierdzenie instalacji sprzętu.")
        print(f"=====================================\n")

    elif "/command" in topic:
        parts = topic.split("/")
        if len(parts) >= 2:
            uuid_str = parts[-2]
            command = data.get("command")
            print(f"\n[{time.strftime('%X')}] ---> ODEBRANO KOMENDĘ <--")
            if command == "ON":
                print(f"[UUID: {uuid_str}]  💡💡💡 KLIK: ŚWIATŁO ZOSTAŁO WŁĄCZONE 💡💡💡")
            elif command == "OFF":
                print(f"[UUID: {uuid_str}]  🌑🌑🌑 KLIK: ŚWIATŁO ZGASŁO 🌑🌑🌑")
            print(f"----------------------------------------")


if __name__ == "__main__":
    print(f"[{time.strftime('%X')}] Symulator włączników oświetlenia w gotowości!")
    
    # Kompatybilność z paho-mqtt v1 i v2
    if hasattr(mqtt, 'CallbackAPIVersion'):
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="LightManager-Sim")
    else:
        client = mqtt.Client(client_id="LightManager-Sim")
        
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nWyłączanie symulatora.")
        client.disconnect()
    except Exception as e:
        print(f"Błąd uruchomienia: {e}")
