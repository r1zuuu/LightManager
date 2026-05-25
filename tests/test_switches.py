def test_create_switch(client):
    # Krok 1: Próba stworzenia urządzenia
    response = client.post("/switches/", json={"name": "Kuchnia Główna"})

    # Assert A: Status HTTP to 201 Created
    assert response.status_code == 201

    data = response.json()
    # Assert B: Poprawnie zapisane nazewnictwo i UUID
    assert "id" in data
    assert data["name"] == "Kuchnia Główna"
    assert data["is_on"] is False


def test_get_switches_empty(client):
    response = client.get("/switches/")
    assert response.status_code == 200
    assert response.json() == []


def test_update_switch_state(client):
    # Krok 1: Tworzymy sprzęt bazowy
    create_response = client.post("/switches/", json={"name": "Salon"})
    switch_id = create_response.json()["id"]

    # Krok 2: Odpalenie sprzętu (Włączenie)
    turn_on_response = client.patch(
        f"/switches/{switch_id}/state", json={"is_on": True}
    )
    assert turn_on_response.status_code == 200

    data_on = turn_on_response.json()
    assert data_on["is_on"] is True
    assert data_on["last_turned_on"] is not None

    # Krok 3: Wyłączenie sprzętu
    turn_off_response = client.patch(
        f"/switches/{switch_id}/state", json={"is_on": False}
    )
    assert turn_off_response.status_code == 200

    data_off = turn_off_response.json()
    assert data_off["is_on"] is False
    assert data_off["last_turned_on"] is None
    # Skoro od włączenia minęło ułamek milisekundy do wyłączenia, czas total() musi być lekko większy bądź równy 0
    assert data_off["total_time_seconds"] >= 0.0
