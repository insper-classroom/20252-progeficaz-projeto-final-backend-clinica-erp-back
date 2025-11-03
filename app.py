from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId  
import time
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask_bcrypt import Bcrypt

load_dotenv('.cred')

mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
db_name = os.getenv('DB_NAME', 'clinica')
jwt_secret = os.getenv('JWT_SECRET', 'clinica_erp_secret_key_2025')

def connect_db():
    try:
        client = MongoClient(mongo_uri)
        db = client[db_name]
        return db
    except Exception as e:
        print(f"Erro ao conectar ao MongoDB: {e}")
        return None

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
bcrypt = Bcrypt(app)

def generate_token(username):
    """Gera um token JWT para o usuário"""
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=24),  # Token expira em 24 horas
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, jwt_secret, algorithm='HS256')
    # Garante que retorna string (PyJWT 2.x retorna string diretamente)
    return token if isinstance(token, str) else token.decode('utf-8')

def token_required(f):
    """Decorator para proteger rotas que requerem autenticação"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Verifica se o token foi enviado no header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Formato esperado: "Bearer <token>"
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({"erro": "Token inválido. Formato esperado: Bearer <token>"}), 401
        
        if not token:
            return jsonify({"erro": "Token de autenticação não fornecido"}), 401
        
        try:
            # Decodifica e valida o token
            data = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            current_user = data['username']
            
            # Verifica se o usuário existe no banco e é admin
            db = connect_db()
            if db is None:
                return jsonify({"erro": "Erro ao conectar ao banco de dados"}), 500
            
            collection = db['admins']
            admin = collection.find_one({"username": current_user, "role": "admin"})
            
            if not admin:
                return jsonify({"erro": "Acesso negado"}), 403
                
        except jwt.ExpiredSignatureError:
            return jsonify({"erro": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"erro": "Token inválido"}), 401
        
        return f(*args, **kwargs)
    
    return decorated

@app.route('/auth/login', methods=['POST'])
def login():
    """Endpoint de login para admin"""
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({"erro": "Dados de login não fornecidos"}), 400
        
        username = dados.get('username')
        password = dados.get('password')
        
        if not username or not password:
            return jsonify({"erro": "Username e password são obrigatórios"}), 400
        
        # Conecta ao banco de dados
        db = connect_db()
        if db is None:
            return jsonify({"erro": "Erro ao conectar ao banco de dados"}), 500
        
        # Busca o admin no banco
        collection = db['admins']
        admin = collection.find_one({"username": username, "role": "admin"})
        
        if not admin:
            return jsonify({"erro": "Credenciais inválidas"}), 401
        
        # Verifica a senha usando bcrypt
        if not bcrypt.check_password_hash(admin['password'], password):
            return jsonify({"erro": "Credenciais inválidas"}), 401
        
        # Gera o token JWT
        token = generate_token(username)
        return jsonify({
            "mensagem": "Login realizado com sucesso",
            "token": token,
            "username": username
        }), 200
    
    except Exception as e:
        return jsonify({"erro": f"Erro ao processar login: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint.

    Returns JSON with service status and whether the DB is reachable.
    """
    
    # quick DB connectivity check
    db = connect_db()
    db_ok = db is not None

    status = {
        "status": "ok" if db_ok else "degraded",
    }
    code = 200 if db_ok else 500
    return status, code

# Médicos
@app.route('/medicos', methods=['GET'])
@token_required
def get_medicos():
    db = connect_db()
    if db is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    try:
        collection = db['medicos']
        medicos_cursor = collection.find({})  
        medicos = []
        for medico in medicos_cursor:
            medico['_id'] = str(medico['_id'])  
            medicos.append(medico)

        if not medicos:
            return {"erro": "Nenhum médico encontrado"}, 404
        return {"medicos": medicos}, 200
    except Exception as e:
        return {"erro": f"Erro ao consultar médicos: {str(e)}"}, 500
    
@app.route('/medicos/<string:id>', methods=['GET'])
@token_required
def get_medico_id(id):
    db = connect_db()
    if db is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    try:
        if not ObjectId.is_valid(id):
            return {"erro": "ID inválido"}, 400

        collection = db['medicos']
        medico = collection.find_one({"_id": ObjectId(id)})

        if not medico:
            return {"erro": "Médico não encontrado"}, 404

        medico['_id'] = str(medico['_id'])  
        return {"medico": medico}, 200
    except Exception as e:
        return {"erro": f"Erro ao consultar médico: {str(e)}"}, 500
@app.route('/medicos', methods=['POST'])
@token_required
def post_medico():
    db = connect_db()
    if db is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    try:
        dados = request.get_json()

        campos_obrigatorios = ["nome", "cpf", "crm", "especialidade"]
        for campo in campos_obrigatorios:
            if campo not in dados or not dados[campo]:
                return {"erro": f"Campo '{campo}' é obrigatório"}, 400

        collection = db['medicos']

        if collection.find_one({"cpf": dados["cpf"]}):
            return {"erro": "Já existe um médico com esse CPF"}, 400
        if collection.find_one({"crm": dados["crm"]}):
            return {"erro": "Já existe um médico com esse CRM"}, 400

        novo_medico = {
            "nome": dados["nome"],
            "cpf": dados["cpf"],
            "crm": dados["crm"],
            "especialidade": dados["especialidade"],
            "horarios": {} 
        }

        resultado = collection.insert_one(novo_medico)

        return {
            "mensagem": "Médico criado com sucesso",
            "id": str(resultado.inserted_id)
        }, 201

    except Exception as e:
        return {"erro": f"Erro ao criar médico: {str(e)}"}, 500


@app.route('/medicos/<id>', methods=['PUT'])
@token_required
def put_medico(id):
    db = connect_db()
    if db is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    try:
        if not ObjectId.is_valid(id):
            return {"erro": "ID inválido"}, 400

        dados = request.get_json()
        if not dados:
            return {"erro": "O corpo da requisição deve conter os dados do médico"}, 400

        campos_validos = ["nome", "cpf", "crm", "especialidade"]
        atualizacoes = {k: v for k, v in dados.items() if k in campos_validos}

        if not atualizacoes:
            return {"erro": "Nenhum campo válido para atualização"}, 400

        collection = db['medicos']
        medico = collection.find_one({"_id": ObjectId(id)})

        if not medico:
            return {"erro": "Médico não encontrado"}, 404

        collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": atualizacoes}
        )

        return {"mensagem": "Dados do médico atualizados com sucesso"}, 200

    except Exception as e:
        return {"erro": f"Erro ao atualizar médico: {str(e)}"}, 500

    
@app.route('/medicos/<id>', methods=['DELETE'])
@token_required
def delete_medico(id):
    db = connect_db()
    if db is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    try:
        if not ObjectId.is_valid(id):
            return {"erro": "ID inválido"}, 400

        collection = db['medicos']
        result = collection.delete_one({"_id": ObjectId(id)})

        if result.deleted_count == 0:
            return {"erro": "Médico não encontrado"}, 404

        return {"mensagem": "Médico deletado com sucesso"}, 200

    except Exception as e:
        return {"erro": f"Erro ao deletar médico: {str(e)}"}, 500
    
# PACIENTES
@app.route('/pacientes', methods=['GET'])
@token_required
def get_pacientes():
    db = connect_db()
    if db is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    try:
        collection = db['pacientes']
        pacientes_cursor = collection.find()
        pacientes = []
        for p in pacientes_cursor:
            p['_id'] = str(p['_id'])
            pacientes.append(p)

        if not pacientes:
            return {"erro": "Nenhum paciente encontrado"}, 404
        return {"pacientes": pacientes}, 200

    except Exception as e:
        return {"erro": f"Erro ao consultar pacientes: {str(e)}"}, 500


@app.route('/pacientes/<id>', methods=['GET'])
@token_required
def get_paciente_id(id):
    db = connect_db()
    if db is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    try:
        collection = db['pacientes']
        paciente = collection.find_one({"_id": ObjectId(id)})
        if not paciente:
            return {"erro": "Paciente não encontrado"}, 404

        paciente['_id'] = str(paciente['_id'])
        return {"paciente": paciente}, 200
    except Exception as e:
        return {"erro": f"Erro ao buscar paciente: {str(e)}"}, 500


@app.route('/pacientes', methods=['POST'])
@token_required
def post_paciente():
    db = connect_db()
    if db is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    try:
        data = request.get_json()
        nome = data.get('nome')
        cpf = data.get('cpf')
        celular = data.get('celular')
        idade = data.get('idade')

        if not all([nome, cpf, celular, idade]):
            return {"erro": "Todos os campos (nome, cpf, celular, idade) são obrigatórios"}, 400

        novo_paciente = {
            "nome": nome,
            "cpf": cpf,
            "celular": celular,
            "idade": idade,
            "consultas": {}
        }

        collection = db['pacientes']
        result = collection.insert_one(novo_paciente)

        return {"mensagem": "Paciente cadastrado com sucesso", "id": str(result.inserted_id)}, 201
    except Exception as e:
        return {"erro": f"Erro ao cadastrar pacient ,.l´ç76e: {str(e)}"}, 500


@app.route('/pacientes/<id>', methods=['PUT'])
@token_required
def put_paciente(id):
    db = connect_db()
    if db is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    try:

        if not ObjectId.is_valid(id):
            return {"erro": "ID inválido"}, 400

        dados = request.get_json()
        if not dados:
            return {"erro": "O corpo da requisição deve conter os dados do paciente"}, 400

        campos_validos = ["nome", "cpf", "celular", "idade"]
        atualizacoes = {k: v for k, v in dados.items() if k in campos_validos}

        if not atualizacoes:
            return {"erro": "Nenhum campo válido para atualização"}, 400

        collection = db['pacientes']
        paciente = collection.find_one({"_id": ObjectId(id)})

        if not paciente:
            return {"erro": "Paciente não encontrado"}, 404

        collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": atualizacoes}
        )

        return {"mensagem": "Dados do paciente atualizados com sucesso"}, 200

    except Exception as e:
        return {"erro": f"Erro ao atualizar paciente: {str(e)}"}, 500
@app.route('/pacientes/<id>', methods=['DELETE'])
@token_required
def delete_paciente(id):
    db = connect_db()
    if db is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    try:
        if not ObjectId.is_valid(id):
            return {"erro": "ID inválido"}, 400

        collection = db['pacientes']
        result = collection.delete_one({"_id": ObjectId(id)})

        if result.deleted_count == 0:
            return {"erro": "Paciente não encontrado"}, 404

        return {"mensagem": "Paciente deletado com sucesso"}, 200

    except Exception as e:
        return {"erro": f"Erro ao deletar paciente: {str(e)}"}, 500

# MÉDICOS - HORÁRIOS
@app.route('/medicos/<id>/horarios', methods=['POST'])
@token_required
def post_horarios_medico(id):
    """Cria novos horários (ou dias inteiros) para o médico"""
    db = connect_db()
    if db is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    try:
        if not ObjectId.is_valid(id):
            return {"erro": "ID inválido"}, 400

        dados = request.get_json()
        if not dados or not isinstance(dados, dict):
            return {"erro": "O corpo da requisição deve ser um dicionário JSON"}, 400

        collection = db['medicos']
        medico = collection.find_one({"_id": ObjectId(id)})

        if not medico:
            return {"erro": "Médico não encontrado"}, 404

        horarios = medico.get("horarios", {})
        for data, horarios_data in dados.items():
            horarios[data] = horarios_data  # adiciona ou substitui o dia inteiro

        collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"horarios": horarios}}
        )

        return {"mensagem": "Horários adicionados com sucesso"}, 201

    except Exception as e:
        return {"erro": f"Erro ao criar horários: {str(e)}"}, 500


@app.route('/medicos/<id>/horarios', methods=['GET'])
@token_required
def get_horarios_medico(id):
    """Retorna todos os horários de um médico"""
    db = connect_db()
    if db is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    try:
        if not ObjectId.is_valid(id):
            return {"erro": "ID inválido"}, 400

        collection = db['medicos']
        medico = collection.find_one({"_id": ObjectId(id)}, {"_id": 0, "horarios": 1})

        if not medico:
            return {"erro": "Médico não encontrado"}, 404

        return {"horarios": medico.get("horarios", {})}, 200

    except Exception as e:
        return {"erro": f"Erro ao buscar horários: {str(e)}"}, 500


@app.route('/medicos/<id>/horarios', methods=['PUT'])
@token_required
def put_horarios_medico(id):
    """Atualiza apenas um horário específico sem alterar os demais"""
    db = connect_db()
    if db is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    try:
        if not ObjectId.is_valid(id):
            return {"erro": "ID inválido"}, 400

        dados = request.get_json()
        data = dados.get("data")
        hora = dados.get("hora")
        info = dados.get("info")

        if not all([data, hora, info]):
            return {"erro": "Campos 'data', 'hora' e 'info' são obrigatórios"}, 400

        collection = db['medicos']
        result = collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {f"horarios.{data}.{hora}": info}}
        )

        if result.matched_count == 0:
            return {"erro": "Médico não encontrado"}, 404

        return {"mensagem": "Horário atualizado com sucesso"}, 200

    except Exception as e:
        return {"erro": f"Erro ao atualizar horário: {str(e)}"}, 500


@app.route('/medicos/<id>/horarios', methods=['DELETE'])
@token_required
def delete_horarios_medico(id):
    """Remove um horário específico ou um dia inteiro"""
    db = connect_db()
    if db is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    try:
        if not ObjectId.is_valid(id):
            return {"erro": "ID inválido"}, 400

        dados = request.get_json()
        data = dados.get("data")
        hora = dados.get("hora")

        if not data:
            return {"erro": "Campo 'data' é obrigatório"}, 400

        collection = db['medicos']

        if hora:
            update = {"$unset": {f"horarios.{data}.{hora}": ""}}
        else:
            update = {"$unset": {f"horarios.{data}": ""}}

        result = collection.update_one({"_id": ObjectId(id)}, update)

        if result.matched_count == 0:
            return {"erro": "Médico não encontrado"}, 404

        return {"mensagem": "Horário removido com sucesso"}, 200

    except Exception as e:
        return {"erro": f"Erro ao deletar horário: {str(e)}"}, 500
    
# PACIENTES -  CONSULTAS
@app.route('/pacientes/<id>/consultas', methods=['POST'])
@token_required
def post_consultas_paciente(id):
    db = connect_db()
    if db is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    try:
        if not ObjectId.is_valid(id):
            return {"erro": "ID inválido"}, 400

        dados = request.get_json()
        if not dados or not isinstance(dados, dict):
            return {"erro": "O corpo da requisição deve ser um dicionário JSON"}, 400

        collection = db['pacientes']
        paciente = collection.find_one({"_id": ObjectId(id)})

        if not paciente:
            return {"erro": "Paciente não encontrado"}, 404

        consultas = paciente.get("consultas", {})
        for data, consultas_data in dados.items():
            consultas[data] = consultas_data

        collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"consultas": consultas}}
        )

        return {"mensagem": "Consultas adicionadas com sucesso"}, 201

    except Exception as e:
        return {"erro": f"Erro ao criar consultas: {str(e)}"}, 500


@app.route('/pacientes/<id>/consultas', methods=['GET'])
@token_required
def get_consultas_paciente(id):
    db = connect_db()
    if db is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    try:
        if not ObjectId.is_valid(id):
            return {"erro": "ID inválido"}, 400

        collection = db['pacientes']
        paciente = collection.find_one({"_id": ObjectId(id)}, {"_id": 0, "consultas": 1})

        if not paciente:
            return {"erro": "Paciente não encontrado"}, 404

        return {"consultas": paciente.get("consultas", {})}, 200

    except Exception as e:
        return {"erro": f"Erro ao buscar consultas: {str(e)}"}, 500


@app.route('/pacientes/<id>/consultas', methods=['PUT'])
@token_required
def put_consultas_paciente(id):
    db = connect_db()
    if db is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    try:

        if not ObjectId.is_valid(id):
            return {"erro": "ID inválido"}, 400

        data = request.get_json()
        data_consulta = data.get("data")
        hora_consulta = data.get("hora")
        detalhes = data.get("detalhes")

        if not all([data_consulta, hora_consulta, detalhes]):
            return {"erro": "Campos 'data', 'hora' e 'detalhes' são obrigatórios"}, 400

        collection = db['pacientes']
        result = collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {f"consultas.{data_consulta}.{hora_consulta}": detalhes}}
        )

        if result.matched_count == 0:
            return {"erro": "Paciente não encontrado"}, 404

        return {"mensagem": "Consulta atualizada com sucesso"}, 200

    except Exception as e:
        return {"erro": f"Erro ao atualizar consulta: {str(e)}"}, 500


@app.route('/pacientes/<id>/consultas', methods=['DELETE'])
@token_required
def delete_consulta_paciente(id):
    db = connect_db()
    if db is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    try:
        if not ObjectId.is_valid(id):
            return {"erro": "ID inválido"}, 400

        dados = request.get_json()
        data = dados.get("data")
        hora = dados.get("hora")

        if not data:
            return {"erro": "Campo 'data' é obrigatório"}, 400

        collection = db['pacientes']

        if hora:
            update = {"$unset": {f"consultas.{data}.{hora}": ""}}
        else:
            update = {"$unset": {f"consultas.{data}": ""}}

        result = collection.update_one({"_id": ObjectId(id)}, update)

        if result.matched_count == 0:
            return {"erro": "Paciente não encontrado"}, 404

        return {"mensagem": "Consulta removida com sucesso"}, 200

    except Exception as e:
        return {"erro": f"Erro ao deletar consulta: {str(e)}"}, 500


if __name__ == '__main__':
    app.run(debug=True)
