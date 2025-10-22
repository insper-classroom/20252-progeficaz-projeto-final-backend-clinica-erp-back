from flask import Flask, request
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId  

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
def get_medico_id():
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
def put_horarios(id):
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
    
    


if __name__ == '__main__':
    app.run(debug=True)
