"""
Bot principal para agendamento de consultas usando LangChain v1.0.
Versão simplificada com create_agent e Google GenAI.
"""

import os
from typing import List
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from .tools import (
    buscar_medicos, 
    buscar_horarios_disponiveis, 
    confirmar_agendamento, 
    cancelar_agendamento,
    listar_especialidades,
    validar_dados_agendamento
)

class AgendamentoBot:
    """Bot de agendamento de consultas com LangChain v1.0."""
    
    def __init__(self):
        # Carrega variáveis de ambiente
        load_dotenv()
        
        # Verificar se a chave da API está configurada
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY não encontrada. Configure a variável de ambiente GOOGLE_API_KEY.")
        
        # Configurar modelo Google GenAI
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.1,
            google_api_key=api_key
        )
        
        # Configurar ferramentas disponíveis
        self.tools = [
            buscar_medicos,
            buscar_horarios_disponiveis,
            confirmar_agendamento,
            cancelar_agendamento,
            listar_especialidades,
            validar_dados_agendamento
        ]
        
        # Criar agente usando a nova API do LangChain v1.0
        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt="""Você é um assistente virtual especializado em agendamento de consultas médicas.
            
            INSTRUÇÕES:
            1. Seja cordial e profissional
            2. Use as ferramentas disponíveis para ajudar o usuário
            3. Confirme dados antes de agendar consultas
            4. Forneça informações claras e precisas
            
            FUNCIONALIDADES DISPONÍVEIS:
            - Buscar médicos por especialidade
            - Verificar horários disponíveis
            - Agendar consultas
            - Cancelar agendamentos
            - Listar especialidades disponíveis
            - Validar dados de agendamento
            
            ESPECIALIDADES DISPONÍVEIS:
            - Cardiologia, Dermatologia, Ortopedia, Pediatria, Ginecologia, Neurologia, Psicologia, Clínica Geral
            
            FORMATOS DE DATA E HORA:
            - Data: YYYY-MM-DD (ex: 2024-12-25)
            - Horário: HH:MM (ex: 14:30)
            
            Sempre mantenha um tom profissional mas amigável."""
        )
    
    def processar_mensagem(self, mensagem: str) -> str:
        """
        Processa uma mensagem do usuário e retorna a resposta do bot.
        
        Args:
            mensagem: Mensagem do usuário
            
        Returns:
            Resposta do bot
        """
        try:
            # Invocar o agente com a mensagem do usuário
            result = self.agent.invoke({
                "messages": [{"role": "user", "content": mensagem}]
            })
            
            # Extrair a resposta da última mensagem
            if result["messages"]:
                last_message = result["messages"][-1]
                return last_message.content
            
            return "Desculpe, não consegui processar sua mensagem."
            
        except Exception as e:
            return f"Desculpe, ocorreu um erro ao processar sua solicitação: {str(e)}"
    
    def iniciar_conversa(self):
        """Inicia uma conversa interativa com o bot."""
        print("🤖 Bot de Agendamento de Consultas - LangChain v1.0")
        print("Digite 'sair' para encerrar a conversa.\n")
        
        while True:
            try:
                mensagem = input("Você: ").strip()
                
                if mensagem.lower() in ['sair', 'exit', 'quit']:
                    print("Até logo! 👋")
                    break
                
                if not mensagem:
                    continue
                
                print("Bot: ", end="")
                resposta = self.processar_mensagem(mensagem)
                print(resposta)
                print()
                
            except KeyboardInterrupt:
                print("\nAté logo! 👋")
                break
            except Exception as e:
                print(f"Erro: {str(e)}")
                print()
    
    def reset_conversa(self):
        """Reseta o histórico de conversa."""
        print("Histórico de conversa resetado.")