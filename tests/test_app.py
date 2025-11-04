# tests/test_app.py
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import jwt

import app as flask_app_module
from app import app as flask_app

JWT_SECRET = getattr(flask_app_module, "jwt_secret", None) or "clinica_erp_secret_key_2025"
JWT_ALGO = "HS256"
flask_app_module.jwt_secret = JWT_SECRET

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client

def make_token(username="admin", hours=24):
    payload = {
        "username": username,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=hours)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
    return token if isinstance(token, str) else token.decode("utf-8")

# MÉDICOS - CRUD

@patch("app.connect_db")
def test_get_medicos_list(mock_connect_db, client):
    mock_db = MagicMock()
    mock_medicos_coll = MagicMock()
    mock_medicos_coll.find.return_value = [
        {"_id": "1", "nome": "Dr. João", "especialidade": "Cardiologia"},
        {"_id": "2", "nome": "Dra. Maria", "especialidade": "Pediatria"},
    ]
    mock_admins_coll = MagicMock()
    mock_admins_coll.find_one.return_value = {"username": "admin", "role": "admin"}
    def getitem(name):
        if name == "medicos":
            return mock_medicos_coll
        if name == "admins":
            return mock_admins_coll
        return MagicMock()
    mock_db.__getitem__.side_effect = getitem
    mock_connect_db.return_value = mock_db
    token = make_token("admin")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/medicos", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "medicos" in data
    assert isinstance(data["medicos"], list)
    assert any(m["nome"] == "Dr. João" for m in data["medicos"])

@patch("app.connect_db")
def test_post_medicos_create(mock_connect_db, client):
    mock_db = MagicMock()
    mock_coll = MagicMock()
    mock_coll.find_one.side_effect = [None, None]
    mock_coll.insert_one.return_value = MagicMock(inserted_id="123abc")
    mock_admins_coll = MagicMock()
    mock_admins_coll.find_one.return_value = {"username": "admin", "role": "admin"}
    def getitem(name):
        if name == "medicos":
            return mock_coll
        if name == "admins":
            return mock_admins_coll
        return MagicMock()
    mock_db.__getitem__.side_effect = getitem
    mock_connect_db.return_value = mock_db
    token = make_token("admin")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "nome": "Dr. Pedro",
        "cpf": "11122233344",
        "crm": "5555",
        "especialidade": "Ortopedia",
    }
    resp = client.post("/medicos", json=payload, headers=headers)
    assert resp.status_code == 201
    j = resp.get_json()
    assert j["mensagem"] == "Médico criado com sucesso"
    assert "id" in j

@patch("app.connect_db")
def test_get_medico_id(mock_connect_db, client):
    mock_db = MagicMock()
    mock_coll = MagicMock()
    mock_coll.find_one.return_value = {
        "_id": "507f1f77bcf86cd799439011",
        "nome": "Dr. João",
        "especialidade": "Cardiologia",
    }
    mock_admins_coll = MagicMock()
    mock_admins_coll.find_one.return_value = {"username": "admin", "role": "admin"}
    def getitem(name):
        if name == "medicos":
            return mock_coll
        if name == "admins":
            return mock_admins_coll
        return MagicMock()
    mock_db.__getitem__.side_effect = getitem
    mock_connect_db.return_value = mock_db
    token = make_token("admin")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/medicos/507f1f77bcf86cd799439011", headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()["medico"]["nome"] == "Dr. João"

@patch("app.connect_db")
def test_put_medico_update(mock_connect_db, client):
    mock_db = MagicMock()
    mock_coll = MagicMock()
    mock_coll.find_one.return_value = {"_id": "507f1f77bcf86cd799439011", "nome": "Dr. João"}
    mock_coll.update_one.return_value = MagicMock(matched_count=1)
    mock_admins_coll = MagicMock()
    mock_admins_coll.find_one.return_value = {"username": "admin", "role": "admin"}
    def getitem(name):
        if name == "medicos":
            return mock_coll
        if name == "admins":
            return mock_admins_coll
        return MagicMock()
    mock_db.__getitem__.side_effect = getitem
    mock_connect_db.return_value = mock_db
    token = make_token("admin")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"especialidade": "Neurologia"}
    resp = client.put("/medicos/507f1f77bcf86cd799439011", json=payload, headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()["mensagem"] == "Dados do médico atualizados com sucesso"

@patch("app.connect_db")
def test_delete_medico(mock_connect_db, client):
    mock_db = MagicMock()
    mock_coll = MagicMock()
    mock_coll.delete_one.return_value = MagicMock(deleted_count=1)
    mock_admins_coll = MagicMock()
    mock_admins_coll.find_one.return_value = {"username": "admin", "role": "admin"}
    def getitem(name):
        if name == "medicos":
            return mock_coll
        if name == "admins":
            return mock_admins_coll
        return MagicMock()
    mock_db.__getitem__.side_effect = getitem
    mock_connect_db.return_value = mock_db
    token = make_token("admin")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.delete("/medicos/507f1f77bcf86cd799439011", headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()["mensagem"] == "Médico deletado com sucesso"

# MÉDICOS - HORÁRIOS

@patch("app.connect_db")
def test_post_medicos_horarios(mock_connect_db, client):
    mock_db = MagicMock()
    mock_med_coll = MagicMock()
    mock_med_coll.find_one.return_value = {"_id": "507f1f77bcf86cd799439011", "horarios": {}}
    mock_med_coll.update_one.return_value = MagicMock(matched_count=1)
    mock_admins_coll = MagicMock()
    mock_admins_coll.find_one.return_value = {"username": "admin", "role": "admin"}
    def getitem(name):
        if name == "medicos":
            return mock_med_coll
        if name == "admins":
            return mock_admins_coll
        return MagicMock()
    mock_db.__getitem__.side_effect = getitem
    mock_connect_db.return_value = mock_db
    token = make_token("admin")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"2025-11-05": {"09:00": "Disponível", "10:00": "Consulta - Ana"}}
    resp = client.post("/medicos/507f1f77bcf86cd799439011/horarios", json=payload, headers=headers)
    assert resp.status_code == 201
    assert resp.get_json()["mensagem"] == "Horários adicionados com sucesso"

@patch("app.connect_db")
def test_get_medicos_horarios(mock_connect_db, client):
    mock_db = MagicMock()
    mock_med_coll = MagicMock()
    mock_med_coll.find_one.return_value = {"horarios": {"2025-11-05": {"09:00": "Disponível"}}}
    mock_admins_coll = MagicMock()
    mock_admins_coll.find_one.return_value = {"username": "admin", "role": "admin"}
    def getitem(name):
        if name == "medicos":
            return mock_med_coll
        if name == "admins":
            return mock_admins_coll
        return MagicMock()
    mock_db.__getitem__.side_effect = getitem
    mock_connect_db.return_value = mock_db
    token = make_token("admin")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/medicos/507f1f77bcf86cd799439011/horarios", headers=headers)
    assert resp.status_code == 200
    assert "horarios" in resp.get_json()
    assert "2025-11-05" in resp.get_json()["horarios"]

@patch("app.connect_db")
def test_put_medicos_horarios_update(mock_connect_db, client):
    mock_db = MagicMock()
    mock_med_coll = MagicMock()
    mock_med_coll.update_one.return_value = MagicMock(matched_count=1)
    mock_med_coll.find_one.return_value = {"_id": "507f1f77bcf86cd799439011", "horarios": {"2025-11-05": {"10:00": "Consulta - Ana"}}}
    mock_admins_coll = MagicMock()
    mock_admins_coll.find_one.return_value = {"username": "admin", "role": "admin"}
    def getitem(name):
        if name == "medicos":
            return mock_med_coll
        if name == "admins":
            return mock_admins_coll
        return MagicMock()
    mock_db.__getitem__.side_effect = getitem
    mock_connect_db.return_value = mock_db
    token = make_token("admin")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"data": "2025-11-05", "hora": "10:00", "info": "Consulta - Bruno"}
    resp = client.put("/medicos/507f1f77bcf86cd799439011/horarios", json=payload, headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()["mensagem"] == "Horário atualizado com sucesso"

@patch("app.connect_db")
def test_delete_medicos_horarios(mock_connect_db, client):
    mock_db = MagicMock()
    mock_med_coll = MagicMock()
    mock_med_coll.update_one.return_value = MagicMock(matched_count=1)
    mock_med_coll.find_one.return_value = {"_id": "507f1f77bcf86cd799439011", "horarios": {"2025-11-05": {"10:00": "Consulta - Bruno"}}}
    mock_admins_coll = MagicMock()
    mock_admins_coll.find_one.return_value = {"username": "admin", "role": "admin"}
    def getitem(name):
        if name == "medicos":
            return mock_med_coll
        if name == "admins":
            return mock_admins_coll
        return MagicMock()
    mock_db.__getitem__.side_effect = getitem
    mock_connect_db.return_value = mock_db
    token = make_token("admin")
    headers = {"Authorization": f"Bearer {token}"}
    # delete specific hour
    resp = client.delete("/medicos/507f1f77bcf86cd799439011/horarios", json={"data": "2025-11-05", "hora": "10:00"}, headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()["mensagem"] == "Horário removido com sucesso"
    # delete whole day (simulate again)
    resp2 = client.delete("/medicos/507f1f77bcf86cd799439011/horarios", json={"data": "2025-11-05"}, headers=headers)
    assert resp2.status_code == 200

# PACIENTES - CRUD

@patch("app.connect_db")
def test_get_pacientes_list(mock_connect_db, client):
    mock_db = MagicMock()
    mock_pacientes_coll = MagicMock()
    mock_pacientes_coll.find.return_value = [
        {"_id": "1", "nome": "Ana", "idade": 30, "cpf": "111"},
        {"_id": "2", "nome": "Bruno", "idade": 45, "cpf": "222"},
    ]
    mock_admins_coll = MagicMock()
    mock_admins_coll.find_one.return_value = {"username": "admin", "role": "admin"}
    def getitem(name):
        if name == "pacientes":
            return mock_pacientes_coll
        if name == "admins":
            return mock_admins_coll
        return MagicMock()
    mock_db.__getitem__.side_effect = getitem
    mock_connect_db.return_value = mock_db
    token = make_token("admin")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/pacientes", headers=headers)
    assert resp.status_code == 200
    assert "pacientes" in resp.get_json()

@patch("app.connect_db")
def test_post_pacientes_create(mock_connect_db, client):
    mock_db = MagicMock()
    mock_coll = MagicMock()
    mock_coll.insert_one.return_value = MagicMock(inserted_id="999")
    mock_admins_coll = MagicMock()
    mock_admins_coll.find_one.return_value = {"username": "admin", "role": "admin"}
    def getitem(name):
        if name == "pacientes":
            return mock_coll
        if name == "admins":
            return mock_admins_coll
        return MagicMock()
    mock_db.__getitem__.side_effect = getitem
    mock_connect_db.return_value = mock_db
    token = make_token("admin")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"nome": "Carlos", "cpf": "444", "celular": "777", "idade": 28}
    resp = client.post("/pacientes", json=payload, headers=headers)
    assert resp.status_code == 201
    assert resp.get_json()["mensagem"] == "Paciente cadastrado com sucesso"

@patch("app.connect_db")
def test_put_paciente_update(mock_connect_db, client):
    mock_db = MagicMock()
    mock_coll = MagicMock()
    mock_coll.find_one.return_value = {"_id": "507f1f77bcf86cd799439011", "nome": "Ana"}
    mock_coll.update_one.return_value = MagicMock(matched_count=1)
    mock_admins_coll = MagicMock()
    mock_admins_coll.find_one.return_value = {"username": "admin", "role": "admin"}
    def getitem(name):
        if name == "pacientes":
            return mock_coll
        if name == "admins":
            return mock_admins_coll
        return MagicMock()
    mock_db.__getitem__.side_effect = getitem
    mock_connect_db.return_value = mock_db
    token = make_token("admin")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"idade": 31}
    resp = client.put("/pacientes/507f1f77bcf86cd799439011", json=payload, headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()["mensagem"] == "Dados do paciente atualizados com sucesso"

@patch("app.connect_db")
def test_delete_paciente(mock_connect_db, client):
    mock_db = MagicMock()
    mock_coll = MagicMock()
    mock_coll.delete_one.return_value = MagicMock(deleted_count=1)
    mock_admins_coll = MagicMock()
    mock_admins_coll.find_one.return_value = {"username": "admin", "role": "admin"}
    def getitem(name):
        if name == "pacientes":
            return mock_coll
        if name == "admins":
            return mock_admins_coll
        return MagicMock()
    mock_db.__getitem__.side_effect = getitem
    mock_connect_db.return_value = mock_db
    token = make_token("admin")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.delete("/pacientes/507f1f77bcf86cd799439011", headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()["mensagem"] == "Paciente deletado com sucesso"

# PACIENTES - CONSULTAS

@patch("app.connect_db")
def test_post_paciente_consultas(mock_connect_db, client):
    mock_db = MagicMock()
    mock_pat_coll = MagicMock()
    mock_pat_coll.find_one.return_value = {"_id": "507f1f77bcf86cd799439011", "consultas": {}}
    mock_pat_coll.update_one.return_value = MagicMock(matched_count=1)
    mock_admins_coll = MagicMock()
    mock_admins_coll.find_one.return_value = {"username": "admin", "role": "admin"}
    def getitem(name):
        if name == "pacientes":
            return mock_pat_coll
        if name == "admins":
            return mock_admins_coll
        return MagicMock()
    mock_db.__getitem__.side_effect = getitem
    mock_connect_db.return_value = mock_db
    token = make_token("admin")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"2025-11-06": {"14:00": "Consulta com Dr. João"}}
    resp = client.post("/pacientes/507f1f77bcf86cd799439011/consultas", json=payload, headers=headers)
    assert resp.status_code == 201
    assert resp.get_json()["mensagem"] == "Consultas adicionadas com sucesso"

@patch("app.connect_db")
def test_get_paciente_consultas(mock_connect_db, client):
    mock_db = MagicMock()
    mock_pat_coll = MagicMock()
    mock_pat_coll.find_one.return_value = {"consultas": {"2025-11-06": {"14:00": "Consulta com Dr. João"}}}
    mock_admins_coll = MagicMock()
    mock_admins_coll.find_one.return_value = {"username": "admin", "role": "admin"}
    def getitem(name):
        if name == "pacientes":
            return mock_pat_coll
        if name == "admins":
            return mock_admins_coll
        return MagicMock()
    mock_db.__getitem__.side_effect = getitem
    mock_connect_db.return_value = mock_db
    token = make_token("admin")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/pacientes/507f1f77bcf86cd799439011/consultas", headers=headers)
    assert resp.status_code == 200
    assert "consultas" in resp.get_json()
    assert "2025-11-06" in resp.get_json()["consultas"]

@patch("app.connect_db")
def test_put_paciente_consultas_update(mock_connect_db, client):
    mock_db = MagicMock()
    mock_pat_coll = MagicMock()
    mock_pat_coll.update_one.return_value = MagicMock(matched_count=1)
    mock_pat_coll.find_one.return_value = {"_id": "507f1f77bcf86cd799439011", "consultas": {"2025-11-06": {"14:00": "Consulta com Dr. João"}}}
    mock_admins_coll = MagicMock()
    mock_admins_coll.find_one.return_value = {"username": "admin", "role": "admin"}
    def getitem(name):
        if name == "pacientes":
            return mock_pat_coll
        if name == "admins":
            return mock_admins_coll
        return MagicMock()
    mock_db.__getitem__.side_effect = getitem
    mock_connect_db.return_value = mock_db
    token = make_token("admin")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"data": "2025-11-06", "hora": "14:00", "detalhes": "Reagendada para 15:00"}
    resp = client.put("/pacientes/507f1f77bcf86cd799439011/consultas", json=payload, headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()["mensagem"] == "Consulta atualizada com sucesso"

@patch("app.connect_db")
def test_delete_paciente_consultas(mock_connect_db, client):
    mock_db = MagicMock()
    mock_pat_coll = MagicMock()
    mock_pat_coll.update_one.return_value = MagicMock(matched_count=1)
    mock_pat_coll.find_one.return_value = {"_id": "507f1f77bcf86cd799439011", "consultas": {"2025-11-06": {"15:00": "Consulta"}}}
    mock_admins_coll = MagicMock()
    mock_admins_coll.find_one.return_value = {"username": "admin", "role": "admin"}
    def getitem(name):
        if name == "pacientes":
            return mock_pat_coll
        if name == "admins":
            return mock_admins_coll
        return MagicMock()
    mock_db.__getitem__.side_effect = getitem
    mock_connect_db.return_value = mock_db
    token = make_token("admin")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.delete("/pacientes/507f1f77bcf86cd799439011/consultas", json={"data": "2025-11-06", "hora": "15:00"}, headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()["mensagem"] == "Consulta removida com sucesso"

# AUTH - LOGIN

@patch("app.connect_db")
def test_auth_login_success_and_failures(mock_connect_db, client):
    mock_db = MagicMock()
    mock_admins_coll = MagicMock()
    password_hash = flask_app_module.bcrypt.generate_password_hash("Admin@123").decode("utf-8")
    mock_admins_coll.find_one.return_value = {"username": "admin", "password": password_hash, "role": "admin"}
    def getitem(name):
        if name == "admins":
            return mock_admins_coll
        return MagicMock()
    mock_db.__getitem__.side_effect = getitem
    mock_connect_db.return_value = mock_db

    resp = client.post("/auth/login", json={"username": "admin", "password": "Admin@123"})
    assert resp.status_code == 200
    j = resp.get_json()
    assert "token" in j and j["username"] == "admin"

    resp_bad = client.post("/auth/login", json={"username": "admin", "password": "wrong"})
    assert resp_bad.status_code == 401

    resp_missing = client.post("/auth/login", json={"username": "admin"})
    assert resp_missing.status_code == 400

# HEALTH

@patch("app.connect_db")
def test_health_ok(mock_connect_db, client):
    mock_connect_db.return_value = MagicMock()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"

@patch("app.connect_db")
def test_health_degraded(mock_connect_db, client):
    mock_connect_db.return_value = None
    resp = client.get("/health")
    assert resp.status_code == 500
    assert resp.get_json()["status"] == "degraded"
