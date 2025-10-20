# Bot de Agendamento de Consultas - LangChain v1.0

Bot inteligente para agendamento de consultas médicas usando LangChain v1.0 com Google GenAI e API simplificada.

## 🚀 Como Usar

### 1. Configurar API Key

**IMPORTANTE**: Crie um arquivo `.env` na raiz do projeto `lia_bot/` com:

```env
GOOGLE_API_KEY=sua_chave_do_gemini_aqui
```

**Para obter uma chave da API:**
1. Acesse: https://makersuite.google.com/app/apikey
2. Crie uma nova chave de API
3. Copie a chave e substitua `sua_chave_do_gemini_aqui` no arquivo `.env`

**Estrutura do projeto:**
```
lia_bot/
├── .env                    # ← Crie este arquivo com sua chave
├── app/
├── main.py
└── requirements.txt
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt --no-deps
```

### 3. Executar o Bot

#### Interface Web (Recomendado)
```bash
streamlit run streamlit_app.py
```

#### Interface CLI (Para testes)
```bash
python main.py
```

#### Exemplo de Uso
```bash
python exemplo_uso.py
```

## 📁 Estrutura do Projeto

```
lia_bot/
├── app/
│   ├── __init__.py              # Pacote Python
│   ├── bot.py                  # Bot principal com LangChain
│   ├── api_client.py           # Cliente mockado para API
│   ├── tools.py                # Ferramentas LangChain
│   ├── classifiers.py          # Sistema de classificação de intenções
│   ├── prompts.py              # Prompts estruturados
│   └── schemas/
│       ├── __init__.py         # Schemas package
│       └── agendamento.py      # Schemas Pydantic
├── main.py                     # Interface CLI
├── streamlit_app.py            # Interface Web Streamlit
├── exemplo_uso.py              # Exemplos de uso
├── requirements.txt            # Dependências
└── README.md                   # Este arquivo
```

## 🔧 Funcionalidades

### Funcionalidades do Bot
- ✅ **Buscar médicos** por especialidade
- ✅ **Verificar horários** disponíveis
- ✅ **Agendar consultas** com validação
- ✅ **Cancelar agendamentos**
- ✅ **Listar especialidades** disponíveis
- ✅ **Validação de dados** antes do agendamento
- ✅ **Processamento natural** de linguagem
- ✅ **Respostas inteligentes** baseadas no contexto

## 🌐 Interfaces Disponíveis

### Interface Web (Streamlit)
- ✅ **Chat interativo** com histórico
- ✅ **Interface moderna** e responsiva
- ✅ **Componentes visuais** (botões, cards)
- ✅ **Fácil navegação** e uso intuitivo

### Interface CLI
- ✅ **Terminal simples** para testes
- ✅ **Comandos diretos** e rápidos
- ✅ **Ideal para desenvolvimento**

## 🛠️ Arquitetura Técnica

### Componentes Principais

1. **Bot Principal (`bot.py`)**
   - Usa `create_agent` da LangChain v1.0
   - Integração direta com Google GenAI
   - Sistema de ferramentas simplificado

2. **Schemas (`schemas/agendamento.py`)**
   - Modelos Pydantic para validação de dados
   - Estruturas para agendamentos, médicos, horários
   - Validação automática de tipos e formatos

3. **Ferramentas (`tools.py`)**
   - Ferramentas LangChain para operações específicas
   - Integração com API mockada
   - Tratamento de erros robusto

4. **Classificadores (`classifiers.py`)**
   - Classificação de intenções usando Google GenAI
   - Extração de dados estruturados
   - Prompts simplificados

5. **Prompts (`prompts.py`)**
   - Formatação de respostas
   - Templates para diferentes contextos

### Tecnologias Utilizadas
- **LangChain v1.0** com `create_agent`
- **Google GenAI (Gemini 2.5 Flash)** como modelo de linguagem
- **Pydantic** para validação de dados
- **API mockada** para simular sistema de agendamentos
- **Streamlit** para interface web moderna

## 📝 Exemplos de Uso

### Buscar Médicos
```
Usuário: "Quero ver os cardiologistas disponíveis"
Bot: [Lista médicos de cardiologia com IDs e informações]
```

### Agendar Consulta
```
Usuário: "Quero agendar com médico 1, dia 25/12/2024 às 14:30, nome João Silva, telefone 11999999999"
Bot: [Valida dados e confirma agendamento]
```

### Verificar Horários
```
Usuário: "Quais horários tem o médico 2 para amanhã?"
Bot: [Lista horários disponíveis para o médico especificado]
```

## 🔧 Configuração para Produção

1. **Substituir API Mockada**: Trocar `MockAgendamentoAPI` por cliente real
2. **Configurar Banco de Dados**: Implementar persistência real
3. **Configurar Logging**: Adicionar sistema de logs robusto
4. **Configurar Monitoramento**: Implementar métricas e alertas

## 📝 Notas

- Sistema simplificado usando LangChain v1.0 com `create_agent`
- Integração direta com Google GenAI (Gemini 2.5 Flash)
- Processamento natural de linguagem sem classificação complexa
- Validação automática de dados antes de operações críticas
- Tratamento robusto de erros em todas as operações
- Arquitetura modular e extensível para novas funcionalidades
- API mais simples e eficiente comparada às versões anteriores
