"""
Ponto de entrada principal do bot de agendamento.
Interface de linha de comando para testar o bot.
"""

import sys
from app.bot import AgendamentoBot


def main():
    """Função principal para executar o bot."""
    try:
        # Cria instância do bot
        bot = AgendamentoBot()
        
        # Inicia conversa interativa
        bot.iniciar_conversa()
        
    except ValueError as e:
        print(f"ERRO de configuracao: {e}")
        print("DICA: Certifique-se de configurar a GOOGLE_API_KEY no arquivo .env")
        sys.exit(1)
    except Exception as e:
        print(f"ERRO inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
