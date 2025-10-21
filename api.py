from flask import Flask, request
import os
from pymongo import MongoClient
from dotenv import load_dotenv

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

@app.route('/alunos', methods=['GET'])
def get_alunos():
    db = connect_db()
    if db is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    try:
        collection = db['alunos']
        alunos_cursor = collection.find({}, {"_id": 0})  # Remove o campo _id da resposta
        alunos = list(alunos_cursor)

        if not alunos:
            return {"erro": "Nenhum aluno encontrado"}, 404
        return {"alunos": alunos}, 200
    except Exception as e:
        return {"erro": f"Erro ao consultar alunos: {str(e)}"}, 500

if __name__ == '__main__':
    app.run(debug=True)