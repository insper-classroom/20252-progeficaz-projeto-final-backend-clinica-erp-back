"""Script para deletar um usuário admin da collection `users`.

Uso:
    python delete_admin.py --username admin_to_delete

Regras de segurança:
- Não permite deletar o último admin (abortará se houver apenas 1 admin).
- Somente deleta documentos com `role: 'admin'`.
"""
import os
import argparse
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv('.cred')

MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')

if not MONGO_URI or not DB_NAME:
    print('MONGO_URI e DB_NAME precisam estar definidas em .cred ou nas variáveis de ambiente')
    raise SystemExit(1)

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users = db['users']

parser = argparse.ArgumentParser(description='Deletar usuário admin')
parser.add_argument('--username', required=True, help='Username do admin a ser deletado')
args = parser.parse_args()

username = args.username

# Confirmação rápida com contagem de admins
admin_count = users.count_documents({'role': 'admin'})
if admin_count <= 1:
    print('Abortando: há apenas 1 admin no sistema. Crie outro admin antes de deletar.')
    raise SystemExit(1)

res = users.delete_one({'username': username, 'role': 'admin'})
if res.deleted_count == 1:
    print(f"Admin '{username}' deletado com sucesso.")
else:
    print(f"Nenhum admin com username '{username}' foi encontrado.")
