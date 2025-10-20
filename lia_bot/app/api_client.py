"""
Cliente mockado para API de agendamentos.
Simula requisições para buscar horários disponíveis, médicos e confirmar agendamentos.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class MockAgendamentoAPI:
    """Cliente mockado que simula uma API real de agendamentos."""
    
    def __init__(self):
        self.medicos = [
            {"id": 1, "nome": "Dr. João Silva", "especialidade": "Cardiologia"},
            {"id": 2, "nome": "Dra. Maria Santos", "especialidade": "Dermatologia"},
            {"id": 3, "nome": "Dr. Pedro Costa", "especialidade": "Ortopedia"},
            {"id": 4, "nome": "Dra. Ana Oliveira", "especialidade": "Pediatria"},
        ]
    
    def buscar_medicos(self, especialidade: Optional[str] = None) -> List[Dict]:
        """
        Busca médicos disponíveis.
        
        Args:
            especialidade: Filtro por especialidade (opcional)
            
        Returns:
            Lista de médicos disponíveis
        """
        if especialidade:
            return [medico for medico in self.medicos 
                   if especialidade.lower() in medico["especialidade"].lower()]
        return self.medicos
    
    def buscar_horarios_disponiveis(self, medico_id: int, data: str) -> List[Dict]:
        """
        Busca horários disponíveis para um médico em uma data específica.
        
        Args:
            medico_id: ID do médico
            data: Data no formato YYYY-MM-DD
            
        Returns:
            Lista de horários disponíveis
        """
        # Simula horários das 8h às 17h com intervalos de 30min
        horarios = []
        for hora in range(8, 17):
            for minuto in [0, 30]:
                # Simula disponibilidade aleatória (70% de chance)
                if random.random() > 0.3:
                    horarios.append({
                        "horario": f"{hora:02d}:{minuto:02d}",
                        "disponivel": True
                    })
        
        return horarios
    
    def confirmar_agendamento(self, medico_id: int, data: str, horario: str, 
                            paciente_nome: str, paciente_telefone: str) -> Dict:
        """
        Confirma um agendamento.
        
        Args:
            medico_id: ID do médico
            data: Data do agendamento
            horario: Horário do agendamento
            paciente_nome: Nome do paciente
            paciente_telefone: Telefone do paciente
            
        Returns:
            Dados do agendamento confirmado
        """
        medico = next((m for m in self.medicos if m["id"] == medico_id), None)
        
        if not medico:
            return {"erro": "Médico não encontrado"}
        
        agendamento_id = random.randint(1000, 9999)
        
        return {
            "id": agendamento_id,
            "medico": medico["nome"],
            "especialidade": medico["especialidade"],
            "data": data,
            "horario": horario,
            "paciente_nome": paciente_nome,
            "paciente_telefone": paciente_telefone,
            "status": "confirmado",
            "codigo_confirmacao": f"AGD{agendamento_id}"
        }
    
    def cancelar_agendamento(self, agendamento_id: int) -> Dict:
        """
        Cancela um agendamento.
        
        Args:
            agendamento_id: ID do agendamento
            
        Returns:
            Status do cancelamento
        """
        return {
            "agendamento_id": agendamento_id,
            "status": "cancelado",
            "mensagem": "Agendamento cancelado com sucesso"
        }
