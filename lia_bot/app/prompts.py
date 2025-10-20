"""
Prompts simplificados para o bot de agendamento com LangChain v1.0.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List
from app.schemas.agendamento import MedicoSchema, HorarioSchema, AgendamentoSchema, EspecialidadeSchema


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


def create_system_prompt() -> str:
    """Cria o prompt do sistema principal."""
    return """
    Você é um assistente virtual especializado em agendamento de consultas médicas.
    
    INSTRUÇÕES:
    1. Seja cordial e profissional
    2. Forneça informações claras e precisas
    3. Confirme dados antes de agendar consultas
    4. Mantenha foco em assuntos relacionados a agendamento médico
    
    ESPECIALIDADES DISPONÍVEIS:
    - Cardiologia, Dermatologia, Ortopedia, Pediatria, Ginecologia, Neurologia, Psicologia, Clínica Geral
    
    FORMATOS:
    - Data: YYYY-MM-DD (ex: 2024-12-25)
    - Horário: HH:MM (ex: 14:30)
    """


def format_medicos_response(medicos: List[MedicoSchema]) -> str:
    """Formata resposta com lista de médicos."""
    if not medicos:
        return "Desculpe, não encontrei médicos disponíveis para a especialidade solicitada."
    
    medicos_text = "\n".join([
        f"• ID: {m.id} | {m.nome} | {m.especialidade}"
        for m in medicos
    ])
    
    return f"Médicos disponíveis:\n{medicos_text}"


def format_horarios_response(horarios: List[HorarioSchema]) -> str:
    """Formata resposta com lista de horários."""
    if not horarios:
        return "Desculpe, não há horários disponíveis para a data solicitada."
    
    horarios_text = "\n".join([
        f"• {h.horario} - {'Disponível' if h.disponivel else 'Ocupado'}"
        for h in horarios
    ])
    
    return f"Horários disponíveis:\n{horarios_text}"


def format_agendamento_response(agendamento: AgendamentoSchema) -> str:
    """Formata resposta de confirmação de agendamento."""
    return f"""
✅ Agendamento confirmado com sucesso!

📋 Detalhes do Agendamento:
• ID: {agendamento.id}
• Médico: {agendamento.medico_nome}
• Especialidade: {agendamento.especialidade}
• Data: {agendamento.data}
• Horário: {agendamento.horario}
• Paciente: {agendamento.paciente_nome}
• Telefone: {agendamento.paciente_telefone}
• Status: {agendamento.status}
• Código de Confirmação: {agendamento.codigo_confirmacao}

Obrigado por escolher nossos serviços!
"""


def format_especialidades_response(especialidades: List[EspecialidadeSchema]) -> str:
    """Formata resposta com lista de especialidades."""
    especialidades_text = "\n".join([
        f"• {esp.nome} ({esp.quantidade_medicos} médicos disponíveis)"
        for esp in especialidades
    ])
    
    return f"Especialidades disponíveis:\n{especialidades_text}"


def format_ajuda_response() -> str:
    """Formata resposta de ajuda."""
    return """
🤖 Bot de Agendamento de Consultas

📋 Funcionalidades disponíveis:
• Buscar médicos por especialidade
• Verificar horários disponíveis
• Agendar consultas
• Cancelar agendamentos
• Listar especialidades disponíveis

💡 Exemplos de uso:
• "Quero ver os médicos de cardiologia"
• "Quais horários tem o médico 1 para amanhã?"
• "Quero agendar consulta com médico 1, dia 25/12/2024 às 14:30"
• "Quais especialidades vocês têm?"

Como posso ajudar você hoje?
"""


def answer_chat_interaction(message: str, chat_history: List[str] = None) -> str:
    """Gera resposta para interações de chat geral."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", create_system_prompt()),
        ("human", "Usuário: {message}")
    ])
    
    model = get_model()
    chain = prompt | model
    response = chain.invoke({"message": message})
    return response.content