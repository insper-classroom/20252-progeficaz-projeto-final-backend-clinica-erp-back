"""
Sistema de classificação de intenções simplificado para LangChain v1.0.
"""

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from app.schemas.agendamento import CreateAgendamentoSchema


class IntentClassification(BaseModel):
    intent: str = Field(description="""
    Analisa a intenção da mensagem para identificar o que o usuário deseja fazer.

    Possíveis intenções:
    - buscar_medicos: Usuário quer buscar médicos ou especialidades
    - verificar_horarios: Usuário quer verificar horários disponíveis
    - agendar_consulta: Usuário quer agendar uma consulta
    - cancelar_agendamento: Usuário quer cancelar um agendamento
    - listar_especialidades: Usuário quer ver lista de especialidades
    - obter_ajuda: Usuário precisa de ajuda ou informações
    - saudacao: Usuário está cumprimentando
    - despedida: Usuário está se despedindo
    - outros: Qualquer outra intenção não relacionada ao agendamento
    """)


class UserQuery(BaseModel):
    especialidade: str = Field(None, description="Especialidade médica mencionada pelo usuário.")
    medico_id: int = Field(None, description="ID do médico mencionado pelo usuário.")
    data: str = Field(None, description="Data mencionada pelo usuário (formato YYYY-MM-DD).")
    horario: str = Field(None, description="Horário mencionado pelo usuário (formato HH:MM).")
    paciente_nome: str = Field(None, description="Nome do paciente mencionado pelo usuário.")
    paciente_telefone: str = Field(None, description="Telefone do paciente mencionado pelo usuário.")
    agendamento_id: int = Field(None, description="ID do agendamento mencionado pelo usuário.")
    observacoes: str = Field(None, description="Observações ou comentários adicionais.")


# Função para obter modelo configurado
def get_model():
    """Obtém o modelo Google GenAI configurado."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY não encontrada. Configure a variável de ambiente GOOGLE_API_KEY.")
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1,
        google_api_key=api_key
    )


def classify_intent(message: str) -> str:
    """Classifica a intenção da mensagem do usuário."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        Analise a mensagem do usuário e classifique a intenção em uma das seguintes categorias:
        - buscar_medicos: Usuário quer buscar médicos ou especialidades
        - verificar_horarios: Usuário quer verificar horários disponíveis
        - agendar_consulta: Usuário quer agendar uma consulta
        - cancelar_agendamento: Usuário quer cancelar um agendamento
        - listar_especialidades: Usuário quer ver lista de especialidades
        - obter_ajuda: Usuário precisa de ajuda ou informações
        - saudacao: Usuário está cumprimentando
        - despedida: Usuário está se despedindo
        - outros: Qualquer outra intenção não relacionada ao agendamento
        
        Responda apenas com o nome da intenção.
        """),
        ("human", "Mensagem: {message}")
    ])
    
    model = get_model()
    chain = prompt | model
    response = chain.invoke({"message": message})
    return response.content.strip().lower()


def extract_agendamento_data(message: str) -> dict:
    """Extrai dados estruturados para agendamento da mensagem."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        Extraia informações de agendamento da mensagem e retorne em formato JSON:
        {
            "especialidade": "especialidade médica ou null",
            "medico_id": "ID do médico ou null",
            "data": "data no formato YYYY-MM-DD ou null",
            "horario": "horário no formato HH:MM ou null",
            "paciente_nome": "nome do paciente ou null",
            "paciente_telefone": "telefone do paciente ou null",
            "observacoes": "observações ou null"
        }
        
        Se alguma informação não estiver presente, use null.
        Retorne apenas o JSON válido.
        """),
        ("human", "Mensagem: {message}")
    ])
    
    model = get_model()
    chain = prompt | model
    response = chain.invoke({"message": message})
    
    # Parsear JSON da resposta
    import json
    try:
        return json.loads(response.content)
    except:
        return {}


def extract_busca_data(message: str) -> dict:
    """Extrai dados para busca de médicos ou horários."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        Extraia informações de busca da mensagem e retorne em formato JSON:
        {
            "especialidade": "especialidade médica ou null",
            "medico_id": "ID do médico ou null",
            "data": "data no formato YYYY-MM-DD ou null"
        }
        
        Se alguma informação não estiver presente, use null.
        Retorne apenas o JSON válido.
        """),
        ("human", "Mensagem: {message}")
    ])
    
    model = get_model()
    chain = prompt | model
    response = chain.invoke({"message": message})
    
    # Parsear JSON da resposta
    import json
    try:
        return json.loads(response.content)
    except:
        return {}