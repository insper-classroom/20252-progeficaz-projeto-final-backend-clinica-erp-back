import pytest
from unittest.mock import patch, MagicMock
from app import app


@pytest.fixture
def client():
    """Cria um cliente de teste do Flask."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# =======================================================
# ================     MÉDICOS       =====================
# =======================================================

@patch("app.connect_db")
def test_get_medicos_list(mock_connect_db, client):
    """GET /medicos - lista todos os médicos"""
    mock_db = MagicMock()
    mock_medicos = MagicMock()
    mock_medicos.find.return_value = [
        {"_id": "1", "nome": "Dr. João", "especialidade": "Cardiologia"},
        {"_id": "2", "nome": "Dra. Maria", "especialidade": "Pediatria"},
    ]
    mock_db.__getitem__.return_value = mock_medicos
    mock_connect_db.return_value = mock_db

    resp = client.get("/medicos")
    assert resp.status_code == 200
    assert resp.get_json() == {
        "medicos": [
            {"_id": "1", "nome": "Dr. João", "especialidade": "Cardiologia"},
            {"_id": "2", "nome": "Dra. Maria", "especialidade": "Pediatria"},
        ]
    }


@patch("app.connect_db")
def test_post_medicos_create(mock_connect_db, client):
    """POST /medicos - cria novo médico"""
    mock_db = MagicMock()
    mock_coll = MagicMock()
    mock_coll.find_one.side_effect = [None, None]
    result = MagicMock(inserted_id="123abc")
    mock_coll.insert_one.return_value = result
    mock_db.__getitem__.return_value = mock_coll
    mock_connect_db.return_value = mock_db

    payload = {
        "nome": "Dr. Pedro",
        "cpf": "11122233344",
        "crm": "5555",
        "especialidade": "Ortopedia",
    }

    resp = client.post("/medicos", json=payload)
    data = resp.get_json()
    assert resp.status_code == 201
    assert data["mensagem"] == "Médico criado com sucesso"
    assert "id" in data


@patch("app.connect_db")
def test_get_medico_id(mock_connect_db, client):
    """GET /medicos/<id>"""
    mock_db = MagicMock()
    mock_coll = MagicMock()
    mock_coll.find_one.return_value = {
        "_id": "507f1f77bcf86cd799439011",
        "nome": "Dr. João",
        "especialidade": "Cardiologia",
    }
    mock_db.__getitem__.return_value = mock_coll
    mock_connect_db.return_value = mock_db

    resp = client.get("/medicos/507f1f77bcf86cd799439011")
    assert resp.status_code == 200
    assert resp.get_json()["medico"]["nome"] == "Dr. João"


@patch("app.connect_db")
def test_put_medico_update(mock_connect_db, client):
    """PUT /medicos/<id> - atualiza horários do médico"""
    mock_db = MagicMock()
    mock_coll = MagicMock()
    mock_coll.find_one.return_value = {
        "_id": "507f1f77bcf86cd799439011",
        "nome": "Dr. João",
        "horarios": {},
    }
    mock_db.__getitem__.return_value = mock_coll
    mock_connect_db.return_value = mock_db

    payload = {
        "2025-10-30": {
            "09:00": {"status": "livre", "paciente": None}
        }
    }

    resp = client.put("/medicos/507f1f77bcf86cd799439011", json=payload)
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["mensagem"] == "Horários atualizados com sucesso"


@patch("app.connect_db")
def test_delete_medico(mock_connect_db, client):
    """DELETE /medicos/<id> - remove médico"""
    mock_db = MagicMock()
    mock_coll = MagicMock()
    result = MagicMock(deleted_count=1)
    mock_coll.delete_one.return_value = result
    mock_db.__getitem__.return_value = mock_coll
    mock_connect_db.return_value = mock_db

    resp = client.delete("/medicos/507f1f77bcf86cd799439011")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["mensagem"] == "Médico deletado com sucesso"


# =======================================================
# ================     PACIENTES     =====================
# =======================================================

@patch("app.connect_db")
def test_get_pacientes_list(mock_connect_db, client):
    """GET /pacientes - lista todos os pacientes"""
    mock_db = MagicMock()
    mock_pacientes = MagicMock()
    mock_pacientes.find.return_value = [
        {"_id": "1", "nome": "Ana", "idade": 30, "cpf": "111"},
        {"_id": "2", "nome": "Bruno", "idade": 45, "cpf": "222"},
    ]
    mock_db.__getitem__.return_value = mock_pacientes
    mock_connect_db.return_value = mock_db

    resp = client.get("/pacientes")
    assert resp.status_code == 200
    assert "pacientes" in resp.get_json()


@patch("app.connect_db")
def test_get_paciente_id(mock_connect_db, client):
    """GET /pacientes/<id>"""
    mock_db = MagicMock()
    mock_coll = MagicMock()
    mock_coll.find_one.return_value = {
        "_id": "507f1f77bcf86cd799439011",
        "nome": "Ana",
        "idade": 30,
        "cpf": "111",
        "celular": "9999",
    }
    mock_db.__getitem__.return_value = mock_coll
    mock_connect_db.return_value = mock_db

    # usa um ObjectId válido de 24 caracteres
    resp = client.get("/pacientes/507f1f77bcf86cd799439011")
    assert resp.status_code == 200
    assert resp.get_json()["paciente"]["nome"] == "Ana"


@patch("app.connect_db")
def test_post_pacientes_create(mock_connect_db, client):
    """POST /pacientes - cria novo paciente"""
    mock_db = MagicMock()
    mock_coll = MagicMock()
    result = MagicMock(inserted_id="999")
    mock_coll.insert_one.return_value = result
    mock_db.__getitem__.return_value = mock_coll
    mock_connect_db.return_value = mock_db

    payload = {
        "nome": "Carlos",
        "cpf": "444",
        "celular": "777",
        "idade": 28,
    }

    resp = client.post("/pacientes", json=payload)
    data = resp.get_json()
    assert resp.status_code == 201
    assert data["mensagem"] == "Paciente cadastrado com sucesso"


@patch("app.connect_db")
def test_put_paciente_update(mock_connect_db, client):
    """PUT /pacientes/<id> - adiciona/atualiza consulta"""
    mock_db = MagicMock()
    mock_coll = MagicMock()
    result = MagicMock(matched_count=1)
    mock_coll.update_one.return_value = result
    mock_db.__getitem__.return_value = mock_coll
    mock_connect_db.return_value = mock_db

    payload = {
        "data": "2025-10-30",
        "hora": "09:00",
        "detalhes": {"status": "confirmado", "medico": "Dr. João"},
    }

    resp = client.put("/pacientes/507f1f77bcf86cd799439011", json=payload)
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["mensagem"] == "Consulta adicionada/atualizada com sucesso"


@patch("app.connect_db")
def test_delete_paciente(mock_connect_db, client):
    """DELETE /pacientes/<id> - remove paciente"""
    mock_db = MagicMock()
    mock_coll = MagicMock()
    result = MagicMock(deleted_count=1)
    mock_coll.delete_one.return_value = result
    mock_db.__getitem__.return_value = mock_coll
    mock_connect_db.return_value = mock_db

    resp = client.delete("/pacientes/507f1f77bcf86cd799439011")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["mensagem"] == "Paciente deletado com sucesso"


# =======================================================
# ================     HEALTH CHECK   ===================
# =======================================================

@patch("app.connect_db")
def test_health_ok(mock_connect_db, client):
    """GET /health - banco disponível"""
    mock_connect_db.return_value = MagicMock()
    resp = client.get("/health")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["status"] == "ok"


@patch("app.connect_db")
def test_health_fail(mock_connect_db, client):
    """GET /health - falha na conexão com o banco"""
    mock_connect_db.return_value = None
    resp = client.get("/health")
    data = resp.get_json()
    assert resp.status_code == 500
    assert data["status"] == "degraded"
