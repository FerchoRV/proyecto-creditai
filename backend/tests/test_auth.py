from __future__ import annotations

from tests.conftest import unique_email, unique_id


def asesor_payload(**overrides):
    data = {
        "nombre": "Ana Asesora",
        "tipo_identificacion": "CC",
        "numero_identificacion": unique_id(),
        "correo": unique_email("asesor"),
        "password": "secreto123",
        "rol": "asesor",
    }
    data.update(overrides)
    return data


def cliente_payload(**overrides):
    data = {
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
    data.update(overrides)
    return data


def test_register_asesor(client):
    payload = asesor_payload()
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201, res.text
    body = res.json()
    assert "access_token" in body
    assert body["user"]["rol"] == "asesor"
    assert body["user"]["correo"] == payload["correo"]
    assert "password" not in body["user"]
    assert "password_hash" not in body["user"]


def test_register_cliente(client):
    payload = cliente_payload()
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["user"]["rol"] == "cliente"
    assert body["user"]["tipo_prestamo"] == "libranza"
    assert float(body["user"]["salario"]) == 3500000


def test_register_cliente_missing_fields(client):
    payload = asesor_payload(rol="cliente")
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 422


def test_register_duplicate_email(client):
    payload = asesor_payload()
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    dup = asesor_payload(correo=payload["correo"])
    res = client.post("/api/v1/auth/register", json=dup)
    assert res.status_code == 409


def test_register_duplicate_identificacion(client):
    payload = asesor_payload()
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    dup = asesor_payload(
        tipo_identificacion=payload["tipo_identificacion"],
        numero_identificacion=payload["numero_identificacion"],
    )
    res = client.post("/api/v1/auth/register", json=dup)
    assert res.status_code == 409


def test_login_ok(client):
    payload = asesor_payload()
    client.post("/api/v1/auth/register", json=payload)
    res = client.post(
        "/api/v1/auth/login",
        json={"correo": payload["correo"], "password": payload["password"]},
    )
    assert res.status_code == 200, res.text
    assert "access_token" in res.json()


def test_login_wrong_password(client):
    payload = asesor_payload()
    client.post("/api/v1/auth/register", json=payload)
    res = client.post(
        "/api/v1/auth/login",
        json={"correo": payload["correo"], "password": "incorrecta99"},
    )
    assert res.status_code == 401
    assert "incorrectos" in res.json()["detail"].lower()


def test_me_with_token(client):
    payload = cliente_payload()
    reg = client.post("/api/v1/auth/register", json=payload).json()
    token = reg["access_token"]
    res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert res.json()["correo"] == payload["correo"]


def test_me_without_token(client):
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401
