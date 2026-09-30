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


def test_cliente_no_puede_invitar(client):
    _, auth = register_cliente(client)
    res = client.post(
        "/api/v1/invitations",
        headers=auth_header(auth["access_token"]),
        json={"correo": unique_email("otro")},
    )
    assert res.status_code == 403


def test_invitar_requiere_correo_o_id(client):
    _, auth = register_asesor(client)
    res = client.post(
        "/api/v1/invitations",
        headers=auth_header(auth["access_token"]),
        json={},
    )
    assert res.status_code == 422


def test_invitar_cliente_existente_vincula_inmediato(client):
    _, asesor = register_asesor(client)
    cliente_payload, cliente = register_cliente(client)

    res = client.post(
        "/api/v1/invitations",
        headers=auth_header(asesor["access_token"]),
        json={"correo": cliente_payload["correo"]},
    )
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["estado"] == "vinculada"
    assert body["solicitud"]["estado"] == "recibido"
    assert body["solicitud"]["cliente_id"] == cliente["user"]["id"]
    assert body["solicitud"]["asesor_id"] == asesor["user"]["id"]


def test_invitar_pendiente_luego_registro_vincula(client):
    _, asesor = register_asesor(client)
    correo = unique_email("futuro")
    numero = unique_id()

    res = client.post(
        "/api/v1/invitations",
        headers=auth_header(asesor["access_token"]),
        json={
            "correo": correo,
            "tipo_identificacion": "CC",
            "numero_identificacion": numero,
        },
    )
    assert res.status_code == 201, res.text
    inv = res.json()
    assert inv["estado"] == "pendiente"
    assert inv["solicitud"]["cliente_id"] is None

    _, cliente = register_cliente(
        client,
        correo=correo,
        numero_identificacion=numero,
        tipo_identificacion="CC",
    )

    listed = client.get(
        "/api/v1/invitations",
        headers=auth_header(asesor["access_token"]),
    )
    assert listed.status_code == 200
    match = next(i for i in listed.json() if i["id"] == inv["id"])
    assert match["estado"] == "vinculada"
    assert match["solicitud"]["cliente_id"] == cliente["user"]["id"]

    cliente_sols = client.get(
        "/api/v1/solicitudes",
        headers=auth_header(cliente["access_token"]),
    )
    assert cliente_sols.status_code == 200
    assert any(s["id"] == inv["solicitud_id"] for s in cliente_sols.json())


def test_multi_solicitud_mismo_cliente(client):
    _, asesor = register_asesor(client)
    cliente_payload, cliente = register_cliente(client)

    for _ in range(2):
        res = client.post(
            "/api/v1/invitations",
            headers=auth_header(asesor["access_token"]),
            json={"correo": cliente_payload["correo"]},
        )
        assert res.status_code == 201

    sols = client.get(
        "/api/v1/solicitudes",
        headers=auth_header(asesor["access_token"]),
    ).json()
    linked = [s for s in sols if s["cliente_id"] == cliente["user"]["id"]]
    assert len(linked) == 2


def test_cliente_con_varios_asesores(client):
    _, a1 = register_asesor(client)
    _, a2 = register_asesor(client)
    cliente_payload, cliente = register_cliente(client)

    for asesor in (a1, a2):
        res = client.post(
            "/api/v1/invitations",
            headers=auth_header(asesor["access_token"]),
            json={"correo": cliente_payload["correo"]},
        )
        assert res.status_code == 201

    sols = client.get(
        "/api/v1/solicitudes",
        headers=auth_header(cliente["access_token"]),
    ).json()
    assert len(sols) == 2
    asesor_ids = {s["asesor_id"] for s in sols}
    assert asesor_ids == {a1["user"]["id"], a2["user"]["id"]}


def test_asesor_lista_invitaciones(client):
    _, asesor = register_asesor(client)
    client.post(
        "/api/v1/invitations",
        headers=auth_header(asesor["access_token"]),
        json={"correo": unique_email("pend")},
    )
    res = client.get(
        "/api/v1/invitations",
        headers=auth_header(asesor["access_token"]),
    )
    assert res.status_code == 200
    assert len(res.json()) >= 1
    assert "estado" in res.json()[0]
