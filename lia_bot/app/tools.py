"""
Ferramentas LangChain para o bot de agendamento.
Define as funções que o agente pode usar para interagir com a API de agendamentos.
"""

from langchain.tools import tool
from typing import List, Optional
from .api_client import MockAgendamentoAPI
from .schemas.agendamento import MedicoSchema, HorarioSchema, AgendamentoSchema, EspecialidadeSchema, CreateAgendamentoSchema
from .prompts import (
    format_medicos_response, 
    format_horarios_response, 
    format_agendamento_response,
    format_especialidades_response
)

# Instância global do cliente API mockado
api_client = MockAgendamentoAPI()


@tool
def buscar_medicos(especialidade: str = None) -> str:
    """
    Busca médicos disponíveis por especialidade.
    
    Args:
        especialidade: Especialidade desejada (opcional)
        
    Returns:
        Lista de médicos disponíveis em formato string
    """
    try:
        medicos_data = api_client.buscar_medicos(especialidade)
        medicos = [MedicoSchema(**medico) for medico in medicos_data]
        return format_medicos_response(medicos)
    except Exception as e:
        return f"Erro ao buscar médicos: {str(e)}"


@tool
def buscar_horarios_disponiveis(medico_id: int, data: str) -> str:
    """
    Busca horários disponíveis para um médico em uma data específica.
    
    Args:
        medico_id: ID do médico
        data: Data no formato YYYY-MM-DD
        
    Returns:
        Lista de horários disponíveis em formato string
    """
    try:
        horarios_data = api_client.buscar_horarios_disponiveis(medico_id, data)
        horarios = [HorarioSchema(**horario, medico_id=medico_id) for horario in horarios_data]
        return format_horarios_response(horarios)
    except Exception as e:
        return f"Erro ao buscar horários: {str(e)}"


@tool
def confirmar_agendamento(medico_id: int, data: str, horario: str, 
                         paciente_nome: str, paciente_telefone: str, 
                         observacoes: str = None) -> str:
    """
    Confirma um agendamento com os dados fornecidos.
    
    Args:
        medico_id: ID do médico
        data: Data do agendamento (YYYY-MM-DD)
        horario: Horário do agendamento (HH:MM)
        paciente_nome: Nome completo do paciente
        paciente_telefone: Telefone do paciente
        observacoes: Observações adicionais (opcional)
        
    Returns:
        Confirmação do agendamento ou erro
    """
    try:
        agendamento_data = api_client.confirmar_agendamento(
            medico_id, data, horario, paciente_nome, paciente_telefone
        )
        
        if "erro" in agendamento_data:
            return f"Erro no agendamento: {agendamento_data['erro']}"
        
        agendamento = AgendamentoSchema(**agendamento_data, observacoes=observacoes)
        return format_agendamento_response(agendamento)
    except Exception as e:
        return f"Erro ao confirmar agendamento: {str(e)}"


@tool
def cancelar_agendamento(agendamento_id: int) -> str:
    """
    Cancela um agendamento existente.
    
    Args:
        agendamento_id: ID do agendamento a ser cancelado
        
    Returns:
        Status do cancelamento
    """
    try:
        resultado = api_client.cancelar_agendamento(agendamento_id)
        return f"Agendamento {agendamento_id} cancelado com sucesso. {resultado.get('mensagem', '')}"
    except Exception as e:
        return f"Erro ao cancelar agendamento: {str(e)}"


@tool
def listar_especialidades() -> str:
    """
    Lista todas as especialidades médicas disponíveis.
    
    Returns:
        Lista de especialidades em formato string
    """
    try:
        # Obter médicos para contar especialidades
        medicos_data = api_client.buscar_medicos()
        
        # Contar médicos por especialidade
        especialidades_count = {}
        for medico in medicos_data:
            especialidade = medico["especialidade"]
            especialidades_count[especialidade] = especialidades_count.get(especialidade, 0) + 1
        
        # Criar lista de especialidades
        especialidades = [
            EspecialidadeSchema(
                nome=esp,
                quantidade_medicos=count
            )
            for esp, count in especialidades_count.items()
        ]
        
        return format_especialidades_response(especialidades)
    except Exception as e:
        return f"Erro ao listar especialidades: {str(e)}"


@tool
def validar_dados_agendamento(medico_id: int, data: str, horario: str, 
                             paciente_nome: str, paciente_telefone: str) -> str:
    """
    Valida os dados fornecidos para agendamento antes da confirmação.
    
    Args:
        medico_id: ID do médico
        data: Data do agendamento (YYYY-MM-DD)
        horario: Horário do agendamento (HH:MM)
        paciente_nome: Nome completo do paciente
        paciente_telefone: Telefone do paciente
        
    Returns:
        Status da validação
    """
    try:
        # Verificar se médico existe
        medicos = api_client.buscar_medicos()
        medico_existe = any(medico["id"] == medico_id for medico in medicos)
        
        if not medico_existe:
            return "Erro: Médico não encontrado. Verifique o ID do médico."
        
        # Verificar se horário está disponível
        horarios = api_client.buscar_horarios_disponiveis(medico_id, data)
        horario_disponivel = any(
            h["horario"] == horario and h["disponivel"] 
            for h in horarios
        )
        
        if not horario_disponivel:
            return f"Erro: Horário {horario} não está disponível para a data {data}."
        
        # Validar formato do telefone (básico)
        if not paciente_telefone.replace("+", "").replace("-", "").replace("(", "").replace(")", "").replace(" ", "").isdigit():
            return "Erro: Formato de telefone inválido."
        
        if len(paciente_nome.strip()) < 2:
            return "Erro: Nome do paciente deve ter pelo menos 2 caracteres."
        
        return "Dados válidos. Pronto para confirmar o agendamento."
        
    except Exception as e:
        return f"Erro na validação: {str(e)}"
