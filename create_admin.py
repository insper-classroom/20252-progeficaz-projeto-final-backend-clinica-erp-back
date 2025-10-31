"""Script para criar o primeiro usuário admin na collection `users`.

Uso:
    python create_admin.py --username admin --password S3nh@Segura

Requer que a variável de ambiente MONGO_URI e DB_NAME estejam definidas (o projeto usa `.cred`).
"""
import os
import argparse
from pymongo import MongoClient
from dotenv import load_dotenv
import bcrypt

load_dotenv('.cred')

MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')

if not MONGO_URI or not DB_NAME:
    print('MONGO_URI e DB_NAME precisam estar definidas em .cred ou nas variáveis de ambiente')
    raise SystemExit(1)

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users = db['users']

parser = argparse.ArgumentParser(description='Criar usuário admin')
parser.add_argument('--username', required=True)
parser.add_argument('--password', required=True)
args = parser.parse_args()

username = args.username
password = args.password

if users.find_one({'username': username}):
    print(f"Usuário '{username}' já existe. Nenhuma ação tomada.")
    raise SystemExit(1)

# Hash da senha com bcrypt
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

user_doc = {
    'username': username,
    'password': hashed,
    'role': 'admin'
}

res = users.insert_one(user_doc)
print(f"Admin criado com id: {res.inserted_id}")
