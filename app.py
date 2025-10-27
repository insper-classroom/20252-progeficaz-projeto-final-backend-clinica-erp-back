from flask import Flask, request
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId  
import time

load_dotenv('.cred')

mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
db_name = os.getenv('DB_NAME', 'clinica')

def connect_db():
    try:
        client = MongoClient(mongo_uri)
        db = client[db_name]
        return db
    except Exception as e:
        print(f"Erro ao conectar ao MongoDB: {e}")
        return None

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint.

    Returns JSON with service status, uptime (seconds) and whether the DB is reachable.
    """
    
    # quick DB connectivity check
    db = connect_db()
    db_ok = db is not None

    status = {
        "status": "ok" if db_ok else "degraded",
        "database": "ok" if db_ok else "unreachable"
    }
    code = 200 if db_ok else 500
    return status, code


@app.route('/medicos', methods=['GET'])
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
def put_medico(id):
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

        horarios_atualizados = medico.get("horarios", {})
        for data, horarios in dados.items():
            if not isinstance(horarios, dict):
                return {"erro": f"Os horários da data '{data}' devem ser um dicionário"}, 400

            if data not in horarios_atualizados:
                horarios_atualizados[data] = {}

            for hora, info in horarios.items():
                if not isinstance(info, dict) or "status" not in info or "paciente" not in info:
                    return {"erro": f"O horário '{hora}' em '{data}' deve conter 'status' e 'paciente'"}, 400
                horarios_atualizados[data][hora] = info

        collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"horarios": horarios_atualizados}}
        )

        return {"mensagem": "Horários atualizados com sucesso"}, 200

    except Exception as e:
        return {"erro": f"Erro ao atualizar horários: {str(e)}"}, 500
    
@app.route('/medicos/<id>', methods=['DELETE'])
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


@app.route('/pacientes/<paciente_id>', methods=['GET'])
def get_paciente_id(paciente_id):
    db = connect_db()
    if db is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    try:
        collection = db['pacientes']
        paciente = collection.find_one({"_id": ObjectId(paciente_id)})
        if not paciente:
            return {"erro": "Paciente não encontrado"}, 404

        paciente['_id'] = str(paciente['_id'])
        return {"paciente": paciente}, 200
    except Exception as e:
        return {"erro": f"Erro ao buscar paciente: {str(e)}"}, 500


@app.route('/pacientes', methods=['POST'])
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
        return {"erro": f"Erro ao cadastrar paciente: {str(e)}"}, 500


@app.route('/pacientes/<paciente_id>', methods=['PUT'])
def put_paciente(paciente_id):
    db = connect_db()
    if db is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    try:
        data = request.get_json()
        data_consulta = data.get("data")  
        hora_consulta = data.get("hora")  
        detalhes = data.get("detalhes")   

        if not all([data_consulta, hora_consulta, detalhes]):
            return {"erro": "Campos 'data', 'hora' e 'detalhes' são obrigatórios"}, 400

        collection = db['pacientes']

        result = collection.update_one(
            {"_id": ObjectId(paciente_id)},
            {"$set": {f"consultas.{data_consulta}.{hora_consulta}": detalhes}}
        )

        if result.matched_count == 0:
            return {"erro": "Paciente não encontrado"}, 404

        return {"mensagem": "Consulta adicionada/atualizada com sucesso"}, 200
    except Exception as e:
        return {"erro": f"Erro ao atualizar consultas: {str(e)}"}, 500
@app.route('/pacientes/<id>', methods=['DELETE'])
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
    


if __name__ == '__main__':
    app.run(debug=True)
