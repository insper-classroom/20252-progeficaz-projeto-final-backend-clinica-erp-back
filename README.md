# API - Sistema de Gerenciamento de Clínica

## Visão Geral

API REST desenvolvida em Flask para gerenciamento de clínicas médicas. O sistema permite o cadastro e gestão de médicos, pacientes, horários de atendimento e consultas agendadas.

**Deploy** `34.226.205.72`(api - backend)

**Base URL:** `http://localhost:5000`

**Banco de Dados:** MongoDB

**CORS:** Habilitado para todas as origens

---

## Quick Start

### Pré-requisitos

- Python 3.8 ou superior instalado
- MongoDB instalado e em execução
- Git (para clonar o repositório)

### Como Rodar

1. **Clone o repositório**
   ```bash
   git clone <url-do-repositorio>
   cd 20252-progeficaz-projeto-final-backend-clinica-erp-back
   ```

2. **Crie e ative um ambiente virtual**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**
   
   Crie um arquivo `.cred` na raiz do projeto com:
   ```env
   MONGO_URI=mongodb://localhost:27017/
   DB_NAME=clinica
   ```

5. **Certifique-se de que o MongoDB está rodando**
   ```bash
   # Windows
   net start MongoDB

   # Linux
   sudo systemctl start mongod

   # Mac
   brew services start mongodb-community
   ```

6. **Execute a aplicação**
   ```bash
   python app.py
   ```

7. **Teste a API**
   
   Acesse no navegador ou use curl:
   ```bash
   curl http://localhost:5000/health
   ```

A API estará disponível em `http://localhost:5000`

---

## Autenticação JWT

A API utiliza autenticação JWT (JSON Web Token) para proteger as rotas. Todas as rotas, exceto `/auth/login` e `/health`, requerem um token válido.

### Criar Usuário Admin

Antes de usar a API, é necessário criar o usuário admin no banco de dados:

```bash
python create_admin.py
```

Este script criará um admin com:
- **Username:** `admin`
- **Password:** `Admin@123`
- **Role:** `admin`

O script é idempotente - pode ser executado múltiplas vezes sem criar duplicatas.

### Login

Para obter um token JWT, faça uma requisição de login:

```http
POST http://localhost:5000/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "Admin@123"
}
```

**Resposta de sucesso (200):**
```json
{
  "mensagem": "Login realizado com sucesso",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "username": "admin"
}
```

**Resposta de erro (401):**
```json
{
  "erro": "Credenciais inválidas"
}
```

### Usar o Token nas Requisições

Todas as requisições para rotas protegidas devem incluir o token JWT no header `Authorization`:

```http
Authorization: Bearer <seu_token_jwt>
```

**Exemplo completo:**

```http
GET http://localhost:5000/medicos
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json
```

### Token Expiração

- O token JWT expira em **24 horas** após a geração
- Após expirar, será necessário fazer login novamente
- Se uma requisição retornar erro 401 (não autorizado), faça login novamente para obter um novo token

### Rotas Protegidas

Todas as rotas abaixo requerem autenticação JWT:

- **Médicos:** GET, POST, PUT, DELETE `/medicos` e `/medicos/<id>`
- **Horários:** GET, POST, PUT, DELETE `/medicos/<id>/horarios`
- **Pacientes:** GET, POST, PUT, DELETE `/pacientes` e `/pacientes/<id>`
- **Consultas:** GET, POST, PUT, DELETE `/pacientes/<id>/consultas`

### Rotas Públicas

As seguintes rotas não requerem autenticação:

- `POST /auth/login` - Login
- `GET /health` - Health check

### Exemplos com cURL

**Login:**
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123"}'
```

**Usar token em requisição:**
```bash
curl -X GET http://localhost:5000/medicos \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json"
```

### Exemplos com JavaScript (Fetch)

```javascript
// Login
const loginResponse = await fetch('http://localhost:5000/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'admin',
    password: 'Admin@123'
  })
});

const loginData = await loginResponse.json();
const token = loginData.token;

// Usar token em requisições protegidas
const medicosResponse = await fetch('http://localhost:5000/medicos', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

const medicos = await medicosResponse.json();
```

### Erros de Autenticação

**401 Unauthorized:**
- Token não fornecido
- Token inválido
- Token expirado
- Credenciais inválidas no login

**403 Forbidden:**
- Usuário não é admin
- Token válido mas sem permissões

---

## Postman Collection

Para facilitar o teste da API, disponibilizamos uma collection do Postman com todos os endpoints configurados.

### Importar Collection

Você pode importar a collection de duas formas:

#### Opção 1: Importar arquivo JSON

1. Baixe o arquivo `Clinica_ERP_API.postman_collection.json` deste repositório
2. Abra o Postman
3. Clique em **Import** no canto superior esquerdo
4. Selecione o arquivo JSON baixado
5. A collection aparecerá na sua sidebar

#### Opção 2: Criar manualmente

Crie uma nova collection no Postman chamada "Clinica ERP API" com a seguinte estrutura:

**Variáveis da Collection:**
- `base_url`: `http://localhost:5000`
- `token`: (será preenchido após fazer login - veja seção Autenticação JWT)
- `medico_id`: (será preenchido após criar um médico)
- `paciente_id`: (será preenchido após criar um paciente)

**Importante:** Para usar a collection no Postman, primeiro:
1. Faça login em `POST /auth/login` para obter o token
2. Salve o token na variável `token` da collection
3. Configure o header `Authorization: Bearer {{token}}` em todas as requisições protegidas

**Pastas e Endpoints:**

```
📁 Clinica ERP API
  📁 Health Check
    ├─ GET Health Check
  📁 Autenticação
    ├─ POST Login
  📁 Médicos
    ├─ GET Listar Médicos
    ├─ GET Buscar Médico por ID
    ├─ POST Criar Médico
    ├─ PUT Atualizar Médico
    └─ DELETE Deletar Médico
  📁 Horários de Médicos
    ├─ GET Listar Horários
    ├─ POST Adicionar Horários
    ├─ PUT Atualizar Horário
    └─ DELETE Remover Horário
  📁 Pacientes
    ├─ GET Listar Pacientes
    ├─ GET Buscar Paciente por ID
    ├─ POST Criar Paciente
    ├─ PUT Atualizar Paciente
    └─ DELETE Deletar Paciente
  📁 Consultas de Pacientes
    ├─ GET Listar Consultas
    ├─ POST Adicionar Consultas
    ├─ PUT Atualizar Consulta
    └─ DELETE Remover Consulta
```

### Exemplos de Requisições

#### Health Check
```http
GET {{base_url}}/health
```

#### Criar Médico
```http
POST {{base_url}}/medicos
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "nome": "Dra. Ana Martins",
  "cpf": "123.456.789-00",
  "crm": "123456-SP",
  "especialidade": "Cardiologia"
}
```

**Nota:** Substitua `{{token}}` pelo token JWT obtido no login. No Postman, você pode criar uma variável de ambiente `token` para facilitar.

#### Adicionar Horários
```http
POST {{base_url}}/medicos/{{medico_id}}/horarios
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "2025-11-05": {
    "08:00": {"status": "disponível", "paciente": "nenhum"},
    "08:30": {"status": "disponível", "paciente": "nenhum"},
    "09:00": {"status": "disponível", "paciente": "nenhum"}
  }
}
```

#### Criar Paciente
```http
POST {{base_url}}/pacientes
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "nome": "Maria Santos",
  "cpf": "111.222.333-44",
  "celular": "(11) 99999-9999",
  "idade": 35
}
```

#### Agendar Consulta
```http
POST {{base_url}}/pacientes/{{paciente_id}}/consultas
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "2025-11-05": {
    "08:00": {
      "medico": "Dra. Ana Martins",
      "especialidade": "Cardiologia",
      "status": "confirmado"
    }
  }
}
```



## Sumário de Endpoints

### Health Check

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Verifica o status da API e conectividade com o banco de dados |

### Médicos

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/medicos` | Lista todos os médicos cadastrados |
| GET | `/medicos/<id>` | Busca um médico específico por ID |
| POST | `/medicos` | Cadastra um novo médico |
| PUT | `/medicos/<id>` | Atualiza dados de um médico |
| DELETE | `/medicos/<id>` | Remove um médico |

### Horários de Médicos

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/medicos/<id>/horarios` | Lista todos os horários de um médico |
| POST | `/medicos/<id>/horarios` | Adiciona horários disponíveis para um médico |
| PUT | `/medicos/<id>/horarios` | Atualiza um horário específico |
| DELETE | `/medicos/<id>/horarios` | Remove horários de um médico |

### Pacientes

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/pacientes` | Lista todos os pacientes cadastrados |
| GET | `/pacientes/<id>` | Busca um paciente específico por ID |
| POST | `/pacientes` | Cadastra um novo paciente |
| PUT | `/pacientes/<id>` | Atualiza dados de um paciente |
| DELETE | `/pacientes/<id>` | Remove um paciente |

### Consultas de Pacientes

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/pacientes/<id>/consultas` | Lista todas as consultas de um paciente |
| POST | `/pacientes/<id>/consultas` | Adiciona consultas para um paciente |
| PUT | `/pacientes/<id>/consultas` | Atualiza uma consulta específica |
| DELETE | `/pacientes/<id>/consultas` | Remove consultas de um paciente |

---

## Documentação Detalhada

### Health Check

#### GET /health

Verifica o status da API e a conectividade com o banco de dados MongoDB.

**Parâmetros:** Nenhum

**Resposta de Sucesso (200):**
```json
{
  "status": "ok"
}
```

**Resposta de Erro (500):**
```json
{
  "status": "degraded"
}
```

---

### Médicos

#### GET /medicos

Lista todos os médicos cadastrados no sistema.

**Parâmetros:** Nenhum

**Resposta de Sucesso (200):**
```json
{
  "medicos": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "nome": "Dra. Ana Martins",
      "cpf": "123.456.789-00",
      "crm": "123456-SP",
      "especialidade": "Cardiologia",
      "horarios": {}
    }
  ]
}
```

**Resposta de Erro:**
- **404:** Nenhum médico encontrado
- **500:** Erro ao conectar ao banco de dados

---

#### GET /medicos/<id>

Busca um médico específico por seu ID.

**Parâmetros de URL:**
- `id` (string, obrigatório): ObjectId do médico no MongoDB

**Resposta de Sucesso (200):**
```json
{
  "medico": {
    "_id": "507f1f77bcf86cd799439011",
    "nome": "Dra. Ana Martins",
    "cpf": "123.456.789-00",
    "crm": "123456-SP",
    "especialidade": "Cardiologia",
    "horarios": {
      "2025-10-20": {
        "09:00": {
          "status": "livre",
          "paciente": "nenhum"
        }
      }
    }
  }
}
```

**Respostas de Erro:**
- **400:** ID inválido
- **404:** Médico não encontrado
- **500:** Erro ao conectar ao banco de dados

---

#### POST /medicos

Cadastra um novo médico no sistema.

**Parâmetros:** Nenhum

**Body (JSON, obrigatório):**
```json
{
  "nome": "Dr. João Silva",
  "cpf": "987.654.321-00",
  "crm": "987654-SP",
  "especialidade": "Dermatologia"
}
```

**Campos Obrigatórios:**
- `nome` (string): Nome completo do médico
- `cpf` (string): CPF do médico (deve ser único)
- `crm` (string): Número do CRM com UF (deve ser único)
- `especialidade` (string): Especialidade médica

**Resposta de Sucesso (201):**
```json
{
  "mensagem": "Médico criado com sucesso",
  "id": "507f1f77bcf86cd799439011"
}
```

**Respostas de Erro:**
- **400:** Campo obrigatório ausente
- **400:** Já existe um médico com esse CPF
- **400:** Já existe um médico com esse CRM
- **500:** Erro ao conectar ao banco de dados

---

#### PUT /medicos/<id>

Atualiza os dados básicos de um médico existente.

**Parâmetros de URL:**
- `id` (string, obrigatório): ObjectId do médico

**Body (JSON):**
```json
{
  "nome": "Dr. João Silva Atualizado",
  "cpf": "987.654.321-00",
  "crm": "987654-SP",
  "especialidade": "Dermatologia Clínica"
}
```

**Campos Válidos para Atualização:**
- `nome` (string): Nome completo do médico
- `cpf` (string): CPF do médico
- `crm` (string): Número do CRM com UF
- `especialidade` (string): Especialidade médica

**Resposta de Sucesso (200):**
```json
{
  "mensagem": "Dados do médico atualizados com sucesso"
}
```

**Respostas de Erro:**
- **400:** ID inválido
- **400:** Corpo da requisição vazio ou sem campos válidos
- **404:** Médico não encontrado
- **500:** Erro ao conectar ao banco de dados

---

#### DELETE /medicos/<id>

Remove um médico do sistema.

**Parâmetros de URL:**
- `id` (string, obrigatório): ObjectId do médico

**Parâmetros:** Nenhum

**Resposta de Sucesso (200):**
```json
{
  "mensagem": "Médico deletado com sucesso"
}
```

**Respostas de Erro:**
- **400:** ID inválido
- **404:** Médico não encontrado
- **500:** Erro ao conectar ao banco de dados

---

### Horários de Médicos

#### GET /medicos/<id>/horarios

Lista todos os horários disponíveis de um médico.

**Parâmetros de URL:**
- `id` (string, obrigatório): ObjectId do médico

**Resposta de Sucesso (200):**
```json
{
  "horarios": {
    "2025-10-20": {
      "08:00": {
        "status": "disponível",
        "paciente": "nenhum"
      },
      "08:30": {
        "status": "ocupado",
        "paciente": "Maria Santos"
      }
    },
    "2025-10-21": {
      "09:00": {
        "status": "disponível",
        "paciente": "nenhum"
      }
    }
  }
}
```

**Respostas de Erro:**
- **400:** ID inválido
- **404:** Médico não encontrado
- **500:** Erro ao conectar ao banco de dados

---

#### POST /medicos/<id>/horarios

Adiciona novos horários disponíveis para um médico. Pode adicionar dias inteiros com múltiplos horários.

**Parâmetros de URL:**
- `id` (string, obrigatório): ObjectId do médico

**Body (JSON, obrigatório):**
```json
{
  "2025-10-20": {
    "08:00": {
      "status": "disponível",
      "paciente": "nenhum"
    },
    "08:30": {
      "status": "disponível",
      "paciente": "nenhum"
    },
    "09:00": {
      "status": "disponível",
      "paciente": "nenhum"
    }
  },
  "2025-10-21": {
    "09:00": {
      "status": "disponível",
      "paciente": "nenhum"
    },
    "10:00": {
      "status": "disponível",
      "paciente": "nenhum"
    }
  }
}
```

**Formato:**
- Chaves de primeiro nível: data no formato `YYYY-MM-DD`
- Chaves de segundo nível: hora no formato `HH:MM`
- Valores: objeto com `status` e `paciente`

**Resposta de Sucesso (201):**
```json
{
  "mensagem": "Horários adicionados com sucesso"
}
```

**Respostas de Erro:**
- **400:** ID inválido
- **400:** Corpo da requisição deve ser um dicionário JSON
- **404:** Médico não encontrado
- **500:** Erro ao conectar ao banco de dados

---

#### PUT /medicos/<id>/horarios

Atualiza um horário específico de um médico sem alterar os demais.

**Parâmetros de URL:**
- `id` (string, obrigatório): ObjectId do médico

**Body (JSON, obrigatório):**
```json
{
  "data": "2025-10-20",
  "hora": "08:00",
  "info": {
    "status": "ocupado",
    "paciente": "João Silva"
  }
}
```

**Campos Obrigatórios:**
- `data` (string): Data no formato `YYYY-MM-DD`
- `hora` (string): Hora no formato `HH:MM`
- `info` (object): Objeto com informações do horário

**Resposta de Sucesso (200):**
```json
{
  "mensagem": "Horário atualizado com sucesso"
}
```

**Respostas de Erro:**
- **400:** Campos obrigatórios ausentes
- **404:** Médico não encontrado
- **500:** Erro ao conectar ao banco de dados

---

#### DELETE /medicos/<id>/horarios

Remove horários de um médico. Pode remover um horário específico ou um dia inteiro.

**Parâmetros de URL:**
- `id` (string, obrigatório): ObjectId do médico

**Body para remover horário específico (JSON):**
```json
{
  "data": "2025-10-20",
  "hora": "08:00"
}
```

**Body para remover dia inteiro (JSON):**
```json
{
  "data": "2025-10-20"
}
```

**Campos:**
- `data` (string, obrigatório): Data no formato `YYYY-MM-DD`
- `hora` (string, opcional): Hora no formato `HH:MM`. Se omitido, remove todo o dia.

**Resposta de Sucesso (200):**
```json
{
  "mensagem": "Horário removido com sucesso"
}
```

**Respostas de Erro:**
- **400:** Campo data é obrigatório
- **404:** Médico não encontrado
- **500:** Erro ao conectar ao banco de dados

---

### Pacientes

#### GET /pacientes

Lista todos os pacientes cadastrados no sistema.

**Parâmetros:** Nenhum

**Resposta de Sucesso (200):**
```json
{
  "pacientes": [
    {
      "_id": "507f1f77bcf86cd799439012",
      "nome": "Maria Santos",
      "cpf": "111.222.333-44",
      "celular": "(11) 99999-9999",
      "idade": 35,
      "consultas": {}
    }
  ]
}
```

**Respostas de Erro:**
- **404:** Nenhum paciente encontrado
- **500:** Erro ao conectar ao banco de dados

---

#### GET /pacientes/<id>

Busca um paciente específico por seu ID.

**Parâmetros de URL:**
- `id` (string, obrigatório): ObjectId do paciente no MongoDB

**Resposta de Sucesso (200):**
```json
{
  "paciente": {
    "_id": "507f1f77bcf86cd799439012",
    "nome": "Maria Santos",
    "cpf": "111.222.333-44",
    "celular": "(11) 99999-9999",
    "idade": 35,
    "consultas": {
      "2025-10-20": {
        "10:00": {
          "medico": "Dra. Ana Martins",
          "especialidade": "Cardiologia",
          "status": "confirmado"
        }
      }
    }
  }
}
```

**Respostas de Erro:**
- **404:** Paciente não encontrado
- **500:** Erro ao conectar ao banco de dados

---

#### POST /pacientes

Cadastra um novo paciente no sistema.

**Parâmetros:** Nenhum

**Body (JSON, obrigatório):**
```json
{
  "nome": "Maria Santos",
  "cpf": "111.222.333-44",
  "celular": "(11) 99999-9999",
  "idade": 35
}
```

**Campos Obrigatórios:**
- `nome` (string): Nome completo do paciente
- `cpf` (string): CPF do paciente
- `celular` (string): Número de celular para contato
- `idade` (number): Idade do paciente

**Resposta de Sucesso (201):**
```json
{
  "mensagem": "Paciente cadastrado com sucesso",
  "id": "507f1f77bcf86cd799439012"
}
```

**Respostas de Erro:**
- **400:** Todos os campos são obrigatórios
- **500:** Erro ao conectar ao banco de dados

---

#### PUT /pacientes/<id>

Atualiza os dados básicos de um paciente existente.

**Parâmetros de URL:**
- `id` (string, obrigatório): ObjectId do paciente

**Body (JSON):**
```json
{
  "nome": "Maria Santos Silva",
  "cpf": "111.222.333-44",
  "celular": "(11) 98888-8888",
  "idade": 36
}
```

**Campos Válidos para Atualização:**
- `nome` (string): Nome completo do paciente
- `cpf` (string): CPF do paciente
- `celular` (string): Número de celular
- `idade` (number): Idade do paciente

**Resposta de Sucesso (200):**
```json
{
  "mensagem": "Dados do paciente atualizados com sucesso"
}
```

**Respostas de Erro:**
- **400:** ID inválido
- **400:** Corpo da requisição vazio ou sem campos válidos
- **404:** Paciente não encontrado
- **500:** Erro ao conectar ao banco de dados

---

#### DELETE /pacientes/<id>

Remove um paciente do sistema.

**Parâmetros de URL:**
- `id` (string, obrigatório): ObjectId do paciente

**Parâmetros:** Nenhum

**Resposta de Sucesso (200):**
```json
{
  "mensagem": "Paciente deletado com sucesso"
}
```

**Respostas de Erro:**
- **400:** ID inválido
- **404:** Paciente não encontrado
- **500:** Erro ao conectar ao banco de dados

---

### Consultas de Pacientes

#### GET /pacientes/<id>/consultas

Lista todas as consultas agendadas de um paciente.

**Parâmetros de URL:**
- `id` (string, obrigatório): ObjectId do paciente

**Resposta de Sucesso (200):**
```json
{
  "consultas": {
    "2025-10-20": {
      "10:00": {
        "medico": "Dra. Ana Martins",
        "especialidade": "Cardiologia",
        "status": "confirmado"
      },
      "14:00": {
        "medico": "Dr. João Silva",
        "especialidade": "Dermatologia",
        "status": "realizado"
      }
    },
    "2025-10-25": {
      "09:00": {
        "medico": "Dra. Ana Martins",
        "especialidade": "Cardiologia",
        "status": "confirmado"
      }
    }
  }
}
```

**Respostas de Erro:**
- **400:** ID inválido
- **404:** Paciente não encontrado
- **500:** Erro ao conectar ao banco de dados

---

#### POST /pacientes/<id>/consultas

Adiciona novas consultas para um paciente. Pode adicionar múltiplas consultas em diferentes datas.

**Parâmetros de URL:**
- `id` (string, obrigatório): ObjectId do paciente

**Body (JSON, obrigatório):**
```json
{
  "2025-10-20": {
    "10:00": {
      "medico": "Dra. Ana Martins",
      "especialidade": "Cardiologia",
      "status": "confirmado"
    }
  },
  "2025-10-25": {
    "09:00": {
      "medico": "Dr. João Silva",
      "especialidade": "Dermatologia",
      "status": "confirmado"
    }
  }
}
```

**Formato:**
- Chaves de primeiro nível: data no formato `YYYY-MM-DD`
- Chaves de segundo nível: hora no formato `HH:MM`
- Valores: objeto com informações da consulta

**Resposta de Sucesso (201):**
```json
{
  "mensagem": "Consultas adicionadas com sucesso"
}
```

**Respostas de Erro:**
- **400:** ID inválido
- **400:** Corpo da requisição deve ser um dicionário JSON
- **404:** Paciente não encontrado
- **500:** Erro ao conectar ao banco de dados

---

#### PUT /pacientes/<id>/consultas

Atualiza uma consulta específica de um paciente sem alterar as demais.

**Parâmetros de URL:**
- `id` (string, obrigatório): ObjectId do paciente

**Body (JSON, obrigatório):**
```json
{
  "data": "2025-10-20",
  "hora": "10:00",
  "detalhes": {
    "medico": "Dra. Ana Martins",
    "especialidade": "Cardiologia",
    "status": "realizado"
  }
}
```

**Campos Obrigatórios:**
- `data` (string): Data no formato `YYYY-MM-DD`
- `hora` (string): Hora no formato `HH:MM`
- `detalhes` (object): Objeto com informações da consulta

**Resposta de Sucesso (200):**
```json
{
  "mensagem": "Consulta atualizada com sucesso"
}
```

**Respostas de Erro:**
- **400:** Campos obrigatórios ausentes
- **404:** Paciente não encontrado
- **500:** Erro ao conectar ao banco de dados

---

#### DELETE /pacientes/<id>/consultas

Remove consultas de um paciente. Pode remover uma consulta específica ou todas as consultas de um dia.

**Parâmetros de URL:**
- `id` (string, obrigatório): ObjectId do paciente

**Body para remover consulta específica (JSON):**
```json
{
  "data": "2025-10-20",
  "hora": "10:00"
}
```

**Body para remover todas as consultas de um dia (JSON):**
```json
{
  "data": "2025-10-20"
}
```

**Campos:**
- `data` (string, obrigatório): Data no formato `YYYY-MM-DD`
- `hora` (string, opcional): Hora no formato `HH:MM`. Se omitido, remove todas as consultas do dia.

**Resposta de Sucesso (200):**
```json
{
  "mensagem": "Consulta removida com sucesso"
}
```

**Respostas de Erro:**
- **400:** Campo data é obrigatório
- **404:** Paciente não encontrado
- **500:** Erro ao conectar ao banco de dados

---

## Códigos de Status HTTP

| Código | Descrição |
|--------|-----------|
| 200 | OK - Requisição processada com sucesso |
| 201 | Created - Recurso criado com sucesso |
| 400 | Bad Request - Dados inválidos ou incompletos |
| 404 | Not Found - Recurso não encontrado |
| 500 | Internal Server Error - Erro no servidor ou banco de dados |

---

## Modelos de Dados

### Médico
```json
{
  "_id": "ObjectId",
  "nome": "string",
  "cpf": "string",
  "crm": "string",
  "especialidade": "string",
  "horarios": {
    "YYYY-MM-DD": {
      "HH:MM": {
        "status": "string",
        "paciente": "string"
      }
    }
  }
}
```

### Paciente
```json
{
  "_id": "ObjectId",
  "nome": "string",
  "cpf": "string",
  "celular": "string",
  "idade": "number",
  "consultas": {
    "YYYY-MM-DD": {
      "HH:MM": {
        "medico": "string",
        "especialidade": "string",
        "status": "string"
      }
    }
  }
}
```

---

## Configuração e Execução

### Requisitos

- Python 3.8+
- MongoDB
- Dependências listadas em `requirements.txt`

### Variáveis de Ambiente

Crie um arquivo `.cred` na raiz do projeto com as seguintes variáveis:

```
MONGO_URI=mongodb://localhost:27017/
DB_NAME=clinica
```

### Instalação

```bash
pip install -r requirements.txt
```

### Execução

```bash
python app.py
```

A API estará disponível em `http://localhost:5000`

---

## Observações Importantes

1. **ObjectId:** Todos os IDs retornados são strings representando MongoDB ObjectIds (24 caracteres hexadecimais).

2. **Formato de Data:** Sempre utilizar o formato `YYYY-MM-DD` (exemplo: 2025-10-20).

3. **Formato de Hora:** Sempre utilizar o formato `HH:MM` no padrão 24 horas (exemplo: 14:30).

4. **Validação de CPF e CRM:** O sistema verifica unicidade de CPF e CRM ao cadastrar médicos.

5. **CORS:** A API está configurada para aceitar requisições de qualquer origem.

6. **Estrutura Aninhada:** Horários e consultas são armazenados como objetos aninhados dentro dos documentos de médicos e pacientes, respectivamente.

7. **Operações de Horários:** Ao adicionar horários via POST, se a data já existir, os horários serão substituídos. Para adicionar horários individualmente, utilize o endpoint PUT.

8. **Operações de Consultas:** Similar aos horários, consultas podem ser adicionadas em lote (POST) ou individualmente (PUT).

---

## Exemplos de Uso

### Fluxo Completo: Cadastro de Médico e Paciente com Agendamento

#### 1. Criar um médico
```bash
curl -X POST http://localhost:5000/medicos \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Dra. Ana Martins",
    "cpf": "123.456.789-00",
    "crm": "123456-SP",
    "especialidade": "Cardiologia"
  }'
```

#### 2. Adicionar horários disponíveis ao médico
```bash
curl -X POST http://localhost:5000/medicos/507f1f77bcf86cd799439011/horarios \
  -H "Content-Type: application/json" \
  -d '{
    "2025-11-05": {
      "08:00": {"status": "disponível", "paciente": "nenhum"},
      "08:30": {"status": "disponível", "paciente": "nenhum"},
      "09:00": {"status": "disponível", "paciente": "nenhum"}
    }
  }'
```

#### 3. Cadastrar um paciente
```bash
curl -X POST http://localhost:5000/pacientes \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria Santos",
    "cpf": "111.222.333-44",
    "celular": "(11) 99999-9999",
    "idade": 35
  }'
```

#### 4. Agendar consulta para o paciente
```bash
curl -X POST http://localhost:5000/pacientes/507f1f77bcf86cd799439012/consultas \
  -H "Content-Type: application/json" \
  -d '{
    "2025-11-05": {
      "08:00": {
        "medico": "Dra. Ana Martins",
        "especialidade": "Cardiologia",
        "status": "confirmado"
      }
    }
  }'
```

#### 5. Marcar horário do médico como ocupado
```bash
curl -X PUT http://localhost:5000/medicos/507f1f77bcf86cd799439011/horarios \
  -H "Content-Type: application/json" \
  -d '{
    "data": "2025-11-05",
    "hora": "08:00",
    "info": {
      "status": "ocupado",
      "paciente": "Maria Santos"
    }
  }'
```

---

## Licença

Este projeto foi desenvolvido como parte do curso de Programação Eficaz do Insper.

