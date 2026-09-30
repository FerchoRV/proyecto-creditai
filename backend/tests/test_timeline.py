from __future__ import annotations

from tests.conftest import unique_email, unique_id


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def register_asesor(client, **overrides):
    payload = {
        "nombre": "Ana Asesora",
        "tipo_identificacion": "CC",
        "numero_identificacion": unique_id(),
        "correo": unique_email("asesor"),
        "password": "secreto123",
        "rol": "asesor",
    }
    payload.update(overrides)
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201, res.text
    return payload, res.json()


def register_cliente(client, **overrides):
    payload = {
        "nombre": "Carlos Cliente",
        "tipo_identificacion": "CC",
        "numero_identificacion": unique_id(),
        "correo": unique_email("cliente"),
        "password": "secreto123",
        "rol": "cliente",
        "salario": 3500000,
        "tipo_prestamo": "libranza",
        "monto_prestamo": 20000000,
    }
    payload.update(overrides)
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201, res.text
    return payload, res.json()


def create_linked_solicitud(client):
    _, asesor = register_asesor(client)
    cliente_payload, cliente = register_cliente(client)
    inv = client.post(
        "/api/v1/invitations",
        headers=auth_header(asesor["access_token"]),
        json={"correo": cliente_payload["correo"]},
    )
    assert inv.status_code == 201, inv.text
    return asesor, cliente, inv.json()


def test_solicitud_nueva_tiene_evento_inicial(client):
    asesor, _cliente, inv = create_linked_solicitud(client)
    detalle = client.get(
        f"/api/v1/solicitudes/{inv['solicitud_id']}",
        headers=auth_header(asesor["access_token"]),
    )
    assert detalle.status_code == 200, detalle.text
    body = detalle.json()
    assert body["estado"] == "recibido"
    assert len(body["timeline"]) >= 1
    assert body["timeline"][0]["from_state"] is None
    assert body["timeline"][0]["to_state"] == "recibido"
    assert "en_estudio" in body["transiciones_disponibles"]


def test_asesor_puede_transicionar(client):
    asesor, _cliente, inv = create_linked_solicitud(client)
    sid = inv["solicitud_id"]
    res = client.post(
        f"/api/v1/solicitudes/{sid}/transiciones",
        headers=auth_header(asesor["access_token"]),
        json={"nuevo_estado": "en_estudio", "nota": "Documentos ok"},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["estado"] == "en_estudio"
    assert body["timeline"][-1]["from_state"] == "recibido"
    assert body["timeline"][-1]["to_state"] == "en_estudio"
    assert body["timeline"][-1]["actor_id"] == asesor["user"]["id"]
    assert body["timeline"][-1]["nota"] == "Documentos ok"


def test_transicion_invalida(client):
    asesor, _cliente, inv = create_linked_solicitud(client)
    res = client.post(
        f"/api/v1/solicitudes/{inv['solicitud_id']}/transiciones",
        headers=auth_header(asesor["access_token"]),
        json={"nuevo_estado": "aprobado"},
    )
    assert res.status_code == 400


def test_estado_terminal_no_reabre(client):
    asesor, _cliente, inv = create_linked_solicitud(client)
    sid = inv["solicitud_id"]
    assert (
        client.post(
            f"/api/v1/solicitudes/{sid}/transiciones",
            headers=auth_header(asesor["access_token"]),
            json={"nuevo_estado": "rechazado"},
        ).status_code
        == 200
    )
    res = client.post(
        f"/api/v1/solicitudes/{sid}/transiciones",
        headers=auth_header(asesor["access_token"]),
        json={"nuevo_estado": "en_estudio"},
    )
    assert res.status_code == 400


def test_cliente_solo_lee_timeline(client):
    asesor, cliente, inv = create_linked_solicitud(client)
    sid = inv["solicitud_id"]
    client.post(
        f"/api/v1/solicitudes/{sid}/transiciones",
        headers=auth_header(asesor["access_token"]),
        json={"nuevo_estado": "en_estudio"},
    )

    detalle = client.get(
        f"/api/v1/solicitudes/{sid}",
        headers=auth_header(cliente["access_token"]),
    )
    assert detalle.status_code == 200
    assert detalle.json()["estado"] == "en_estudio"
    assert len(detalle.json()["timeline"]) >= 2
    assert detalle.json()["transiciones_disponibles"] == []

    forbidden = client.post(
        f"/api/v1/solicitudes/{sid}/transiciones",
        headers=auth_header(cliente["access_token"]),
        json={"nuevo_estado": "aprobado"},
    )
    assert forbidden.status_code == 403


def test_asesor_ajeno_no_accede(client):
    _asesor, _cliente, inv = create_linked_solicitud(client)
    _, otro = register_asesor(client)
    res = client.get(
        f"/api/v1/solicitudes/{inv['solicitud_id']}",
        headers=auth_header(otro["access_token"]),
    )
    assert res.status_code == 403
