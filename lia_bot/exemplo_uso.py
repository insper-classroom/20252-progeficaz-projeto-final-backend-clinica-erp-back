"""
Exemplo de uso do bot de agendamento com LangChain v1.0 e Google GenAI.
Demonstra como usar o bot com diferentes tipos de mensagens.
"""

from app.bot import AgendamentoBot


def exemplo_uso():
    """Exemplo de uso do bot de agendamento."""
    
    # Criar instância do bot
    bot = AgendamentoBot()
    
    print("=== EXEMPLO DE USO DO BOT DE AGENDAMENTO ===\n")
    
    # Exemplos de mensagens para testar
    exemplos = [
        "Olá, preciso agendar uma consulta",
        "Quero ver os médicos de cardiologia disponíveis",
        "Quais especialidades vocês têm?",
        "Preciso verificar os horários do médico 1 para 2024-12-25",
        "Quero agendar consulta com médico 1, data 2024-12-25, horário 14:30, nome João Silva, telefone 11999999999",
        "Como posso cancelar um agendamento?",
        "Preciso de ajuda com o sistema"
    ]
    
    for i, mensagem in enumerate(exemplos, 1):
        print(f"--- Exemplo {i} ---")
        print(f"Usuário: {mensagem}")
        resposta = bot.processar_mensagem(mensagem)
        print(f"Bot: {resposta}")
        print()


def exemplo_conversa_interativa():
    """Exemplo de conversa interativa com o bot."""
    
    bot = AgendamentoBot()
    
    print("=== CONVERSA INTERATIVA ===\n")
    
    # Simular uma conversa
    conversa = [
        "Olá!",
        "Quero agendar uma consulta",
        "Sou João Silva, telefone 11999999999",
        "Quero com um cardiologista",
        "Para o dia 2024-12-25 às 14:30",
        "Obrigado!"
    ]
    
    for mensagem in conversa:
        print(f"Usuário: {mensagem}")
        resposta = bot.processar_mensagem(mensagem)
        print(f"Bot: {resposta}")
        print()


if __name__ == "__main__":
    # Executar exemplos
    exemplo_uso()
    print("\n" + "="*50 + "\n")
    exemplo_conversa_interativa()
