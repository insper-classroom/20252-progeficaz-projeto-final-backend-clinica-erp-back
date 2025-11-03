# test_app.py
import pytest
from unittest.mock import patch, MagicMock
from app import app
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    """Cria um cliente de teste do Flask com um JWT válido no header Authorization."""
    app.config["TESTING"] = True
    # chave de teste para gerar token
    app.config["JWT_SECRET_KEY"] = "test-secret-for-unit-tests"

    # criar token no contexto da app
    with app.test_request_context():
        token = create_access_token(identity="admin")

    client = app.test_client()
    # injetar header Authorization em todas as requisições do test client
    client.environ_base.setdefault('HTTP_AUTHORIZATION', f"Bearer {token}")
    yield client


# =======================================================
# ================     MÉDICOS       =====================
# =======================================================

@patch("app.connect_db")
def test_get_medicos_list(mock_connect_db, client):
    """GET /medicos - lista todos os médicos"""
    mock_db = MagicMock()

    # coleção 'medicos' retorna lista de médicos
    mock_medicos_coll = MagicMock()
    mock_medicos_coll.find.return_value = [
        {"_id": "507f1f77bcf86cd799439011", "nome": "Dr. João", "especialidade": "Cardiologia"},
        {"_id": "507f1f77bcf86cd799439012", "nome": "Dra. Maria", "especialidade": "Pediatria"},
    ]

    def getitem(name):
        if name == "medicos":
            return mock_medicos_coll
        return MagicMock()

    mock_db.__getitem__.side_effect = getitem
    mock_connect_db.return_value = mock_db

    resp = client.get("/medicos")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "medicos" in data
    assert len(data["medicos"]) == 2
    assert data["medicos"][0]["nome"] == "Dr. João"


@patch("app.connect_db")
def test_post_medicos_create(mock_connect_db, client):
    """POST /medicos - cria novo médico (admin)"""
    mock_db = MagicMock()

    # users -> usuário admin
    mock_users_coll = MagicMock()
    mock_users_coll.find_one.return_value = {"username": "admin", "role": "admin"}

    # medicos -> comportamento de insert
    mock_medicos_coll = MagicMock()
    mock_medicos_coll.find_one.side_effect = [None, None]
    mock_medicos_coll.insert_one.return_value = MagicMock(inserted_id="123abc")

    def getitem(name):
        if name == "users":
            return mock_users_coll
        if name == "medicos":
            return mock_medicos_coll
        return MagicMock()

    mock_db.__getitem__.side_effect = getitem
    mock_connect_db.return_value = mock_db

    payload = {
        "nome": "Dr. Pedro",
        "cpf": "11122233344",
        "crm": "5555",
        "especialidade": "Ortopedia",
    }

    resp = client.post("/medicos", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
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
def test_put_medico_update_fields(mock_connect_db, client):
    """PUT /medicos/<id> - atualiza dados do médico (checa apenas o status 200)."""
    mock_db = MagicMock()
    mock_users_coll = MagicMock()
    mock_users_coll.find_one.return_value = {"username": "admin", "role": "admin"}
    mock_medicos_coll = MagicMock()
    mock_medicos_coll.find_one.return_value = {"_id": "507f1f77bcf86cd799439011", "nome": "Dr. João"}
    mock_medicos_coll.update_one.return_value = MagicMock(matched_count=1)

    def getitem(name):
        if name == "users":
            return mock_users_coll
        if name == "medicos":
            return mock_medicos_coll
        return MagicMock()

    mock_db.__getitem__.side_effect = getitem
    mock_connect_db.return_value = mock_db

    payload = {"nome": "Dr. João Atualizado", "especialidade": "Neurologia"}
    resp = client.put("/medicos/507f1f77bcf86cd799439011", json=payload)

    assert resp.status_code == 200



@patch("app.connect_db")
def test_delete_medico(mock_connect_db, client):
    """DELETE /medicos/<id> - remove médico"""
    mock_db = MagicMock()
    mock_users_coll = MagicMock()
    mock_users_coll.find_one.return_value = {"username": "admin", "role": "admin"}
    mock_medicos_coll = MagicMock()
    mock_medicos_coll.delete_one.return_value = MagicMock(deleted_count=1)

    def getitem(name):
        if name == "users":
            return mock_users_coll
        if name == "medicos":
            return mock_medicos_coll
        return MagicMock()

    mock_db.__getitem__.side_effect = getitem
    mock_connect_db.return_value = mock_db

    resp = client.delete("/medicos/507f1f77bcf86cd799439011")
    assert resp.status_code == 200


@patch("app.connect_db")
def test_post_medicos_horarios(mock_connect_db, client):
    """POST /medicos/<id>/horarios - adiciona horários"""
    mock_db = MagicMock()
    mock_coll = MagicMock()
    mock_coll.find_one.return_value = {"_id": "507f1f77bcf86cd799439011", "horarios": {}}
    mock_coll.update_one.return_value = MagicMock()
    mock_db.__getitem__.return_value = mock_coll
    mock_connect_db.return_value = mock_db

    payload = {
        "2025-11-10": {
            "09:00": {"status": "livre"}
        }
    }
    resp = client.post("/medicos/507f1f77bcf86cd799439011/horarios", json=payload)
    assert resp.status_code == 201
    assert resp.get_json()["mensagem"] == "Horários adicionados com sucesso"


@patch("app.connect_db")
def test_get_medicos_horarios(mock_connect_db, client):
    """GET /medicos/<id>/horarios"""
    mock_db = MagicMock()
    mock_coll = MagicMock()
    mock_coll.find_one.return_value = {"horarios": {"2025-11-10": {"09:00": {"status": "livre"}}}}
    mock_db.__getitem__.return_value = mock_coll
    mock_connect_db.return_value = mock_db

    resp = client.get("/medicos/507f1f77bcf86cd799439011/horarios")
    assert resp.status_code == 200
    assert "horarios" in resp.get_json()


@patch("app.connect_db")
def test_put_medicos_horario_specific(mock_connect_db, client):
    """PUT /medicos/<id>/horarios - atualiza um horário específico"""
    mock_db = MagicMock()
    mock_coll = MagicMock()
    mock_coll.update_one.return_value = MagicMock(matched_count=1)
    mock_db.__getitem__.return_value = mock_coll
    mock_connect_db.return_value = mock_db

    payload = {"data": "2025-11-10", "hora": "09:00", "info": {"status": "ocupado"}}
    resp = client.put("/medicos/507f1f77bcf86cd799439011/horarios", json=payload)
    assert resp.status_code == 200
    assert resp.get_json()["mensagem"] == "Horário atualizado com sucesso"


@patch("app.connect_db")
def test_delete_medicos_horario(mock_connect_db, client):
    """DELETE /medicos/<id>/horarios - remove horário ou dia"""
    mock_db = MagicMock()
    mock_coll = MagicMock()
    mock_coll.update_one.return_value = MagicMock(matched_count=1)
    mock_db.__getitem__.return_value = mock_coll
    mock_connect_db.return_value = mock_db

    payload = {"data": "2025-11-10", "hora": "09:00"}
    resp = client.delete("/medicos/507f1f77bcf86cd799439011/horarios", json=payload)
    assert resp.status_code == 200
    assert resp.get_json()["mensagem"] == "Horário removido com sucesso"


# =======================================================
# ================     PACIENTES     =====================
# =======================================================

@patch("app.connect_db")
def test_get_pacientes_list(mock_connect_db, client):
    """GET /pacientes - lista todos os pacientes"""
    mock_db = MagicMock()
    mock_pacientes_coll = MagicMock()
    mock_pacientes_coll.find.return_value = [
        {"_id": "1", "nome": "Ana", "idade": 30, "cpf": "111"},
        {"_id": "2", "nome": "Bruno", "idade": 45, "cpf": "222"},
    ]
    mock_db.__getitem__.return_value = mock_pacientes_coll
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

    resp = client.get("/pacientes/507f1f77bcf86cd799439011")
    assert resp.status_code == 200
    assert resp.get_json()["paciente"]["nome"] == "Ana"


@patch("app.connect_db")
def test_post_pacientes_create(mock_connect_db, client):
    """POST /pacientes - cria novo paciente"""
    mock_db = MagicMock()
    mock_coll = MagicMock()
    mock_coll.insert_one.return_value = MagicMock(inserted_id="999")
    mock_db.__getitem__.return_value = mock_coll
    mock_connect_db.return_value = mock_db

    payload = {
        "nome": "Carlos",
        "cpf": "444",
        "celular": "777",
        "idade": 28,
    }

    resp = client.post("/pacientes", json=payload)
    assert resp.status_code == 201
    assert resp.get_json()["mensagem"] == "Paciente cadastrado com sucesso"


@patch("app.connect_db")
def test_put_paciente_update_consulta(mock_connect_db, client):
    """PUT /pacientes/<id>/consultas - atualiza/insere consulta"""
    mock_db = MagicMock()
    mock_coll = MagicMock()
    mock_coll.update_one.return_value = MagicMock(matched_count=1)
    mock_db.__getitem__.return_value = mock_coll
    mock_connect_db.return_value = mock_db

    payload = {
        "data": "2025-11-10",
        "hora": "09:00",
        "detalhes": {"status": "confirmado", "medico": "Dr. João"},
    }

    resp = client.put("/pacientes/507f1f77bcf86cd799439011/consultas", json=payload)
    assert resp.status_code == 200
    assert resp.get_json()["mensagem"] == "Consulta atualizada com sucesso"


@patch("app.connect_db")
def test_post_paciente_consultas_bulk(mock_connect_db, client):
    """POST /pacientes/<id>/consultas - adiciona consultas em lote (dia inteiro)"""
    mock_db = MagicMock()
    mock_coll = MagicMock()
    mock_coll.find_one.return_value = {"_id": "507f1f77bcf86cd799439011", "consultas": {}}
    mock_coll.update_one.return_value = MagicMock()
    mock_db.__getitem__.return_value = mock_coll
    mock_connect_db.return_value = mock_db

    payload = {
        "2025-11-10": {
            "09:00": {"detalhes": "consulta 1"}
        }
    }
    resp = client.post("/pacientes/507f1f77bcf86cd799439011/consultas", json=payload)
    assert resp.status_code == 201
    assert resp.get_json()["mensagem"] == "Consultas adicionadas com sucesso"


@patch("app.connect_db")
def test_delete_paciente_consulta(mock_connect_db, client):
    """DELETE /pacientes/<id>/consultas - remove uma consulta"""
    mock_db = MagicMock()
    mock_coll = MagicMock()
    mock_coll.update_one.return_value = MagicMock(matched_count=1)
    mock_db.__getitem__.return_value = mock_coll
    mock_connect_db.return_value = mock_db

    payload = {"data": "2025-11-10", "hora": "09:00"}
    resp = client.delete("/pacientes/507f1f77bcf86cd799439011/consultas", json=payload)
    assert resp.status_code == 200
    assert resp.get_json()["mensagem"] == "Consulta removida com sucesso"


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
