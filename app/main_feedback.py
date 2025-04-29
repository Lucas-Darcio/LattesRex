import os
import sys
import streamlit as st

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.business_logic.resume_processor import process_resume
from app.business_logic.query_handler import  extract_attributes_chatbot, handle_query_chat

from app.data_access.file_manager import list_curriculos, load_curriculo
#from app.services.email_service import send_email

from app.business_logic.compression_utils import extract_prompt_tags

from app.api.openai_api import extract_related_tags

# Diretório onde os currículos armazenados ficam
CURRICULO_DIR = "curriculos/"

# Caminho para o arquivo JSON
CONSULTAS_DIR = "consultas/"


@st.dialog("Explicação da Avaliação")
def explicacao():
    st.write(f"Voce deve avaliar o LLM tendo em vista a...")

    if st.button("Entendido"):
        st.session_state.explicacaodada = True
        st.rerun()

def main():
    st.set_page_config(
        page_title="Converse com o currículo",
        layout="wide"
    )

    st.title("Converse com o currículo")

    if 'disable_chat_bool' not in st.session_state:
        st.session_state.disable_chat_bool = True  # 'value'


    if "explicacaodada" not in st.session_state:
        explicacao()
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
            curriculo_data = process_resume(
                os.path.join(CURRICULO_DIR, selected_resume))
            curriculo_name = selected_resume
            st.sidebar.write(f"Currículo escolhido: {curriculo_name}")

        if st.button("Confirmar currículo", type="primary"):
            # Escolha final do currículo: preferindo o upload se houver
            print(st.session_state.disable_chat_bool)
            st.session_state.disable_chat_bool = not st.session_state.disable_chat_bool
            print(st.session_state.disable_chat_bool)

    if not st.session_state.disable_chat_bool:

        st.warning(f"curriculo {curriculo_name} carregado!")

    col1, col2 = st.columns(2)
    

    with col1:
            
        # Inicia o o historico de mensagens na sessão
        if "messages" not in st.session_state:
            st.session_state.messages = []

        historico_mensagens = st.container(height=350, border=True)
        
        with historico_mensagens:
            # exibe o historico das mensganes
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            

        form_promtp = st.form("form prompt")
        with form_promtp:
            user_input = st.selectbox("Selecione a sua tarefa ou pergunta:", 
                                  [" Qual é a quantidade e a qualidade dos artigos publicados pelo pesquisador em periódicos indexados de alto impacto?",
                                   "As publicações estão concentradas em revistas ou conferências de relevância na área de atuação?",
                                   "Qual é o número de citações dos artigos do pesquisador em bases como Scopus ou Google Scholar?",
                                   "O pesquisador possui índice h (h-index) ou outros indicadores de impacto significativo na sua área?",
                                   " O pesquisador já liderou ou participou como proponente de projetos financiados por agências de fomento?",
                                   "Qual é o histórico do pesquisador em atrair recursos de pesquisa por meio de editais competitivos?",
                                   "Quantos alunos de mestrado, doutorado e iniciação científica o pesquisador já orientou ou está orientando?",
                                   "Qual é a relevância das produções acadêmicas desenvolvidas por seus orientandos, como publicações ou trabalhos apresentados? ",
                                   "O pesquisador contribui para a formação de alunos na graduação por meio de atividades como orientação de TCC ou projetos de pesquisa? ",
                                   "Qual é o impacto das orientações na carreira acadêmica ou profissional dos alunos formados?",
                                   "O pesquisador participa de redes de colaboração nacionais ou  internacionais relevantes? ",
                                   "Existem evidências de coautorias ou projetos conjuntos com outros pesquisadores de destaque?",
                                   "O pesquisador já ocupou cargos administrativos relevantes (ex.: coordenador de programa de pós-graduação, diretor de instituto, etc.)? ",
                                   "Ele lidera grupos de pesquisa reconhecidos pelo CNPq ou outras instituições?",
                                   "Há evidências de que os resultados das pesquisas do pesquisador geraram impacto social, tecnológico ou econômico? ",
                                   " O pesquisador possui patentes ou outros produtos registrados oriundos de sua pesquisa?",
                                   "O pesquisador foi convidado como palestrante em eventos científicos de prestígio?",
                                   "Ele já recebeu prêmios ou reconhecimentos por sua contribuição científica?"],
                                   index=None,
                                   )
            st.write("Prompt selecionado:", user_input)


            selecionado = st.form_submit_button("Selecionar")
        
        if(selecionado):
            #adiciona a mensagem do usuario ao historico
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Manda o prommpt do usuario para o chat e espera a resposta
            with st.spinner("Carregando..."):
                bot_reply = f"Chatbot: {user_input}"
            
            #Adiciona a mensagem do bot ao historico
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            
            # Força a reexecução para atualizar o histórico imediatamente
            st.rerun()



    with col2:
        form_avaliador = st.form("form_avaliador")
        with form_avaliador:
            
            st.write("Avalie com as seguintes estrelas o aplicativo:")
            selected = st.feedback("stars")

            submitted = st.form_submit_button("enviar")

        if submitted:
        #    st.write("slider", slider_val)
            st.write("stars", selected)


if __name__ == "__main__":
    main()