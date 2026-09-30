from __future__ import annotations

from tests.conftest import unique_email, unique_id


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


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_get_me_requires_auth(client):
    res = client.get("/api/v1/users/me")
    assert res.status_code == 401


def test_get_me_ok(client):
    _, auth = register_asesor(client)
    res = client.get("/api/v1/users/me", headers=auth_header(auth["access_token"]))
    assert res.status_code == 200
    assert res.json()["id"] == auth["user"]["id"]
    assert "password_hash" not in res.json()


def test_update_me_nombre_y_correo(client):
    _, auth = register_asesor(client)
    token = auth["access_token"]
    nuevo_correo = unique_email("nuevo")
    res = client.patch(
        "/api/v1/users/me",
        headers=auth_header(token),
        json={"nombre": "Ana Actualizada", "correo": nuevo_correo},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["nombre"] == "Ana Actualizada"
    assert body["correo"] == nuevo_correo
    assert body["rol"] == "asesor"


def test_update_me_correo_duplicado(client):
    payload_a, _ = register_asesor(client)
    _, auth_b = register_asesor(client)
    res = client.patch(
        "/api/v1/users/me",
        headers=auth_header(auth_b["access_token"]),
        json={"correo": payload_a["correo"]},
    )
    assert res.status_code == 409


def test_update_cliente_campos(client):
    _, auth = register_cliente(client)
    res = client.patch(
        "/api/v1/users/me",
        headers=auth_header(auth["access_token"]),
        json={
            "salario": 4000000,
            "tipo_prestamo": "hipotecario",
            "monto_prestamo": 80000000,
        },
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert float(body["salario"]) == 4000000
    assert body["tipo_prestamo"] == "hipotecario"


def test_asesor_no_puede_enviar_campos_cliente(client):
    _, auth = register_asesor(client)
    res = client.patch(
        "/api/v1/users/me",
        headers=auth_header(auth["access_token"]),
        json={"salario": 1000},
    )
    assert res.status_code == 422


def test_identificacion_inmutable_via_payload_ignorado(client):
    """La identificación no forma parte del schema de update (inmutable)."""
    _, auth = register_asesor(client)
    res = client.patch(
        "/api/v1/users/me",
        headers=auth_header(auth["access_token"]),
        json={"numero_identificacion": "999999"},
    )
    # Extra fields ignored by default in Pydantic v2 → 200 sin cambiar ID
    assert res.status_code == 200
    me = client.get("/api/v1/users/me", headers=auth_header(auth["access_token"]))
    assert me.json()["numero_identificacion"] == auth["user"]["numero_identificacion"]


def test_no_puede_cambiar_rol(client):
    _, auth = register_asesor(client)
    res = client.patch(
        "/api/v1/users/me",
        headers=auth_header(auth["access_token"]),
        json={"rol": "cliente"},
    )
    assert res.status_code == 200
    assert (
        client.get("/api/v1/users/me", headers=auth_header(auth["access_token"])).json()[
            "rol"
        ]
        == "asesor"
    )


def test_forbidden_update_otro_usuario(client):
    _, auth_a = register_asesor(client)
    _, auth_b = register_asesor(client)
    res = client.patch(
        f"/api/v1/users/{auth_b['user']['id']}",
        headers=auth_header(auth_a["access_token"]),
        json={"nombre": "Hack"},
    )
    assert res.status_code == 403


def test_change_password(client):
    payload, auth = register_asesor(client)
    token = auth["access_token"]
    res = client.post(
        "/api/v1/users/me/password",
        headers=auth_header(token),
        json={"password_actual": payload["password"], "password_nueva": "nuevaClave9"},
    )
    assert res.status_code == 200
    bad = client.post(
        "/api/v1/auth/login",
        json={"correo": payload["correo"], "password": payload["password"]},
    )
    assert bad.status_code == 401
    ok = client.post(
        "/api/v1/auth/login",
        json={"correo": payload["correo"], "password": "nuevaClave9"},
    )
    assert ok.status_code == 200


def test_deactivate_blocks_login_and_me(client):
    payload, auth = register_cliente(client)
    token = auth["access_token"]
    res = client.delete("/api/v1/users/me", headers=auth_header(token))
    assert res.status_code == 204

    login = client.post(
        "/api/v1/auth/login",
        json={"correo": payload["correo"], "password": payload["password"]},
    )
    assert login.status_code == 401
    assert "desactiv" in login.json()["detail"].lower()

    me = client.get("/api/v1/users/me", headers=auth_header(token))
    assert me.status_code == 401
