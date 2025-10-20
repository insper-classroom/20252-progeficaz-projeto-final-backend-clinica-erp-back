"""
Schemas para estruturação de dados de agendamento.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CreateAgendamentoSchema(BaseModel):
    """Schema para criação de agendamento."""
    medico_id: int = Field(description="ID do médico")
    data: str = Field(description="Data do agendamento (YYYY-MM-DD)")
    horario: str = Field(description="Horário do agendamento (HH:MM)")
    paciente_nome: str = Field(description="Nome completo do paciente")
    paciente_telefone: str = Field(description="Telefone do paciente")
    observacoes: Optional[str] = Field(None, description="Observações adicionais")


class AgendamentoSchema(BaseModel):
    """Schema para representar um agendamento."""
    id: int
    medico_id: int
    medico_nome: str
    especialidade: str
    data: str
    horario: str
    paciente_nome: str
    paciente_telefone: str
    status: str
    codigo_confirmacao: str
    observacoes: Optional[str] = None


class MedicoSchema(BaseModel):
    """Schema para representar um médico."""
    id: int
    nome: str
    especialidade: str
    disponivel: bool = True


class HorarioSchema(BaseModel):
    """Schema para representar um horário disponível."""
    horario: str
    disponivel: bool
    medico_id: Optional[int] = None


class EspecialidadeSchema(BaseModel):
    """Schema para representar uma especialidade."""
    nome: str
    descricao: Optional[str] = None
    quantidade_medicos: int = 0
