import os
import sys
import streamlit as st

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.business_logic.resume_processor import process_resume
from app.business_logic.query_handler import  final_response_generator_log 
from app.data_access.file_manager import list_curriculos, load_curriculo

# Diretório onde os currículos armazenados ficam
CURRICULO_DIR = "curriculos/"


def main():
    st.set_page_config(
        page_title="Converse com o currículo",
        layout="wide"
    )

    st.title("Converse com o currículo")

    if 'disable_chat_bool' not in st.session_state:
        st.session_state.disable_chat_bool = True  # 'value'

    # disable_chat_bool = True
    curriculo_name = ""

    with st.sidebar:

        passos = '''1 - Envie ou selecione um currículo no formato XML.   
        2 - Confirme a seleção de currículo para que ele vá para o contexto.   
        3 - Utilize o chat para realizar as atividades.   
'''

        # cont_height = 500
        st.header("Escolher Currículo")
        st.markdown(passos)

        # Upload de novo currículo
        uploaded_file = st.sidebar.file_uploader(
            "Faça upload de um currículo (XML)", type="xml")

        # Exibe currículos existentes no diretório
        stored_resumes = list_curriculos(CURRICULO_DIR)
        selected_resume = st.sidebar.selectbox(
            "Ou escolha um currículo existente do nosso banco de dados", stored_resumes)

        if uploaded_file:
            # curriculo_data = load_curriculo(os.path.join(CURRICULO_DIR, selected_resume))
            curriculo_data = process_resume(load_curriculo(uploaded_file))
            curriculo_name = uploaded_file.name
            st.sidebar.write(f"Currículo escolhido: {curriculo_name}")
        else:
            curriculo_data = process_resume(os.path.join(CURRICULO_DIR, selected_resume))
            curriculo_name = selected_resume
            st.sidebar.write(f"Currículo escolhido: {curriculo_name}")

        if st.button("Confirmar currículo", type="primary"):
            # Escolha final do currículo: preferindo o upload se houver
            st.session_state.disable_chat_bool = not st.session_state.disable_chat_bool

    if not st.session_state.disable_chat_bool:
        st.warning(f"curriculo {curriculo_name} carregado!")

    # Inicia o o historico de mensagens na sessão
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # exibe o historico das mensganes
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # esntrando
    user_input = st.chat_input(
        placeholder="Digite sua tarefa ou pergunta...", disabled=st.session_state.disable_chat_bool)
    
    if user_input:
        #adiciona a mensagem do usuario ao historico
        st.session_state.messages.append({"role": "user", "content": user_input})
        

        with st.spinner("Carregando..."):
            bot_reply = final_response_generator_log(user_input, curriculo_data, 122000, curriculo_name)

        #Adiciona a resposta do chatbot ao historico
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

        #atualiza a interface com a nova resposta
        with st.chat_message("user"):
            st.markdown(user_input)
            
        with st.chat_message("assistant"):
            st.markdown(bot_reply)
        
        

if __name__ == "__main__":
    main()
