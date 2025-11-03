"""
Script para criar o usuário admin no banco de dados MongoDB.
Executa: python create_admin.py
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from datetime import datetime

# Carrega variáveis de ambiente
load_dotenv('.cred')

# Configurações do banco de dados
mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
db_name = os.getenv('DB_NAME', 'clinica')

# Credenciais do admin
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'Admin@123'

def connect_db():
    """Conecta ao MongoDB"""
    try:
        client = MongoClient(mongo_uri)
        db = client[db_name]
        return db
    except Exception as e:
        print(f"Erro ao conectar ao MongoDB: {e}")
        return None

def create_admin():
    """Cria o usuário admin no banco de dados"""
    print("=" * 50)
    print("Script de Criação do Admin")
    print("=" * 50)
    
    # Conecta ao banco
    db = connect_db()
    if db is None:
        print("Erro: Não foi possível conectar ao banco de dados.")
        print(f"   Verifique a conexão MongoDB: {mongo_uri}")
        return False
    
    print(f"Conectado ao banco de dados: {db_name}")
    
    # Obtém a collection de admins
    collection = db['admins']
    
    # Verifica se o admin já existe
    existing_admin = collection.find_one({"username": ADMIN_USERNAME})
    
    if existing_admin:
        print(f"Admin '{ADMIN_USERNAME}' já existe no banco de dados.")
        print("   Script idempotente: não será criado novamente.")
        return True
    
    # Gera hash da senha usando bcrypt
    try:
        bcrypt = Bcrypt()
        hashed_password = bcrypt.generate_password_hash(ADMIN_PASSWORD).decode('utf-8')
        print("Senha hashada com sucesso usando bcrypt")
    except Exception as e:
        print(f"Erro ao gerar hash da senha: {e}")
        return False
    
    # Cria o documento do admin
    admin_doc = {
        "username": ADMIN_USERNAME,
        "password": hashed_password,
        "role": "admin",
        "created_at": datetime.utcnow()
    }
    
    # Insere no banco
    try:
        result = collection.insert_one(admin_doc)
        print(f"Admin criado com sucesso!")
        print(f"   ID: {result.inserted_id}")
        print(f"   Username: {ADMIN_USERNAME}")
        print(f"   Role: admin")
        print(f"   Criado em: {admin_doc['created_at']}")
        return True
    except Exception as e:
        print(f"Erro ao inserir admin no banco: {e}")
        return False

if __name__ == '__main__':
    success = create_admin()
    print("=" * 50)
    if success:
        print("Processo concluído com sucesso!")
    else:
        print("Processo concluído com erros.")
    print("=" * 50)
