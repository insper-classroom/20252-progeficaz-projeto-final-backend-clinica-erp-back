"""
Interface Streamlit para o Bot de Agendamento de Consultas.
"""

import streamlit as st
from app.bot import AgendamentoBot

# Configuração da página
st.set_page_config(
    page_title="Bot de Agendamento de Consultas",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar bot
if "bot" not in st.session_state:
    st.session_state.bot = AgendamentoBot()
    st.session_state.messages = []

# Título principal
st.title("🏥 Bot de Agendamento de Consultas")
st.markdown("---")

# Sidebar com informações
with st.sidebar:
    st.header("ℹ️ Informações")
    st.markdown("""
    **Funcionalidades:**
    - Buscar médicos por especialidade
    - Verificar horários disponíveis
    - Agendar consultas
    - Cancelar agendamentos
    """)
    
    st.header("🎯 Comandos Rápidos")
    if st.button("👨‍⚕️ Ver Médicos"):
        st.session_state.messages.append({"role": "user", "content": "médicos"})
    
    if st.button("🕐 Ver Especialidades"):
        st.session_state.messages.append({"role": "user", "content": "especialidades"})
    
    if st.button("📅 Agendar Consulta"):
        st.session_state.messages.append({"role": "user", "content": "agendar"})
    
    if st.button("❓ Ajuda"):
        st.session_state.messages.append({"role": "user", "content": "ajuda"})
    
    if st.button("🗑️ Limpar Chat"):
        st.session_state.messages = []
        st.rerun()

# Container principal do chat
chat_container = st.container()

# Exibir histórico de mensagens
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Input do usuário
if prompt := st.chat_input("Digite sua mensagem aqui..."):
    # Adicionar mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Exibir mensagem do usuário
    with st.chat_message("user"):
        st.write(prompt)
    
    # Processar mensagem e obter resposta do bot
    with st.chat_message("assistant"):
        with st.spinner("Processando..."):
            response = st.session_state.bot.processar_mensagem(prompt)
            st.write(response)
    
    # Adicionar resposta do bot ao histórico
    st.session_state.messages.append({"role": "assistant", "content": response})

# Rodapé
st.markdown("---")
st.markdown("💡 **Dica:** Use os botões da sidebar para comandos rápidos ou digite sua mensagem abaixo.")