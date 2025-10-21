import pytest
from unittest.mock import patch, MagicMock
# Precisa colocar o app corretamente após a criação do app
from app import app

@pytest.fixture
def client():
    """Cria um cliente de teste para a API."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# =======================================================
# ================     MÉDICOS       =====================
# =======================================================

@patch("app.conectar_bd")
def test_get_medicos_list(mock_conectar_bd, client):
    """GET /api/medicos - lista todos os médicos"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        (1, "Dr. João", "Cardiologia"),
        (2, "Dra. Maria", "Pediatria")
    ]
    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_bd.return_value = mock_conn

    response = client.get("/api/medicos")
    assert response.status_code == 200
    assert response.get_json() == [
        {"id": 1, "nome": "Dr. João", "especialidade": "Cardiologia"},
        {"id": 2, "nome": "Dra. Maria", "especialidade": "Pediatria"}
    ]


@patch("app.conectar_bd")
def test_post_medicos_create(mock_conectar_bd, client):
    """POST /api/medicos - cria novo médico"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 3
    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_bd.return_value = mock_conn

    payload = {"nome": "Dr. Pedro", "especialidade": "Ortopedia"}
    response = client.post("/api/medicos", json=payload)

    assert response.status_code == 201
    assert response.get_json() == {"id": 3, "nome": "Dr. Pedro", "especialidade": "Ortopedia"}


@patch("app.conectar_bd")
def test_get_medico_by_id(mock_conectar_bd, client):
    """GET /api/medicos/<id> - retorna médico específico"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1, "Dr. João", "Cardiologia")
    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_bd.return_value = mock_conn

    response = client.get("/api/medicos/1")
    assert response.status_code == 200
    assert response.get_json() == {"id": 1, "nome": "Dr. João", "especialidade": "Cardiologia"}


@patch("app.conectar_bd")
def test_post_medico_update(mock_conectar_bd, client):
    """POST /api/medicos/<id> - atualiza médico"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 1
    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_bd.return_value = mock_conn

    payload = {"nome": "Dr. João Silva", "especialidade": "Cardiologia"}
    response = client.post("/api/medicos/1", json=payload)

    assert response.status_code == 200
    assert response.get_json() == {"id": 1, "nome": "Dr. João Silva", "especialidade": "Cardiologia"}


@patch("app.conectar_bd")
def test_get_medico_disponibilidades(mock_conectar_bd, client):
    """GET /api/medicos/<id>/disponibilidades - lista disponibilidades fixas"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        (1, "09:00", "12:00"),
        (2, "14:00", "18:00")
    ]
    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_bd.return_value = mock_conn

    response = client.get("/api/medicos/1/disponibilidades")
    assert response.status_code == 200
    assert response.get_json() == [
        {"dia_semana": 1, "inicio": "09:00", "fim": "12:00"},
        {"dia_semana": 2, "inicio": "14:00", "fim": "18:00"}
    ]


@patch("app.conectar_bd")
def test_get_medico_slots(mock_conectar_bd, client):
    """GET /api/medicos/<id>/slots - lista horários disponíveis"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        ("2025-10-22T09:00:00",),
        ("2025-10-22T09:30:00",)
    ]
    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_bd.return_value = mock_conn

    response = client.get("/api/medicos/1/slots?date=2025-10-22&slotMinutes=30")
    assert response.status_code == 200
    assert response.get_json() == ["2025-10-22T09:00:00", "2025-10-22T09:30:00"]


# =======================================================
# ================     PACIENTES     =====================
# =======================================================

@patch("app.conectar_bd")
def test_get_pacientes_list(mock_conectar_bd, client):
    """GET /api/pacientes - lista todos os pacientes"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        (1, "Ana", 30, "Particular"),
        (2, "Bruno", 45, "SUS")
    ]
    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_bd.return_value = mock_conn

    response = client.get("/api/pacientes")
    assert response.status_code == 200
    assert response.get_json() == [
        {"id": 1, "nome": "Ana", "idade": 30, "plano": "Particular"},
        {"id": 2, "nome": "Bruno", "idade": 45, "plano": "SUS"}
    ]


@patch("app.conectar_bd")
def test_post_pacientes_create(mock_conectar_bd, client):
    """POST /api/pacientes - cria novo paciente"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 5
    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_bd.return_value = mock_conn

    payload = {"nome": "Carlos", "idade": 28, "plano": "Particular"}
    response = client.post("/api/pacientes", json=payload)

    assert response.status_code == 201
    assert response.get_json() == {"id": 5, "nome": "Carlos", "idade": 28, "plano": "Particular"}


@patch("app.conectar_bd")
def test_get_paciente_by_id(mock_conectar_bd, client):
    """GET /api/pacientes/<id> - retorna paciente específico"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1, "Ana", 30, "Particular")
    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_bd.return_value = mock_conn

    response = client.get("/api/pacientes/1")
    assert response.status_code == 200
    assert response.get_json() == {"id": 1, "nome": "Ana", "idade": 30, "plano": "Particular"}


@patch("app.conectar_bd")
def test_post_paciente_update(mock_conectar_bd, client):
    """POST /api/pacientes/<id> - atualiza paciente"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 1
    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_bd.return_value = mock_conn

    payload = {"nome": "Ana Souza", "idade": 31, "plano": "Particular"}
    response = client.post("/api/pacientes/1", json=payload)

    assert response.status_code == 200
    assert response.get_json() == {"id": 1, "nome": "Ana Souza", "idade": 31, "plano": "Particular"}


# =======================================================
# ================     AGENDAMENTOS   =====================
# =======================================================

@patch("app.conectar_bd")
def test_post_agendamento_create(mock_conectar_bd, client):
    """POST /api/agendamentos - cria novo agendamento"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 10
    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_bd.return_value = mock_conn

    payload = {
        "medico_id": 1,
        "paciente_id": 2,
        "data_hora": "2025-10-22T09:00:00"
    }
    response = client.post("/api/agendamentos", json=payload)

    assert response.status_code == 201
    assert response.get_json() == {
        "id": 10,
        "medico_id": 1,
        "paciente_id": 2,
        "data_hora": "2025-10-22T09:00:00"
    }


# =======================================================
# ================     HEALTH CHECK   ====================
# =======================================================

def test_get_health(client):
    """GET /health - verifica status do servidor"""
    response = client.get("/health")
    assert response.status_code == 200
    json_body = response.get_json()
    assert json_body in ({"status": "ok"}, {"status": "healthy"}) or "status" in json_body
