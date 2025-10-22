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

    
    


if __name__ == '__main__':
    app.run(debug=True)
