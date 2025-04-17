import os
import sys
import tiktoken
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.api.openai_api import extract_related_tags
from app.data_access.file_manager import list_curriculos, load_curriculo
from app.business_logic.resume_processor import process_resume
from app.business_logic.compression_utils import extract_prompt_tags
from app.business_logic.query_handler import  extract_attributes_chatbot, handle_query_chat

# Diretório onde os currículos armazenados ficam
CURRICULO_DIR = "curriculos/"

stored_resumes = list_curriculos(CURRICULO_DIR)

prompts_list = ["Qual é a quantidade e a qualidade dos artigos publicados pelo pesquisador em periódicos indexados de alto impacto?", "As publicações estão concentradas em revistas ou conferências de relevância na área de atuação?", "Qual é o número de citações dos artigos do pesquisador em bases como Scopus ou Google Scholar?",
             "O pesquisador possui índice h (h-index) ou outros indicadores de impacto significativo na sua área?", "O pesquisador já liderou ou participou como proponente de projetos financiados por agências de fomento?", "Qual é o histórico do pesquisador em atrair recursos de pesquisa por meio de editais competitivos?",
             "Quantos alunos de mestrado, doutorado e iniciação científica o pesquisador já orientou ou está orientando?", "Qual é a relevância das produções acadêmicas desenvolvidas por seus orientandos, como publicações ou trabalhos apresentados?",
             "O pesquisador contribui para a formação de alunos na graduação por meio de atividades como orientação de TCC ou projetos de pesquisa?", "Qual é o impacto das orientações na carreira acadêmica ou profissional dos alunos formados?", "O pesquisador participa de redes de colaboração nacionais ou  internacionais relevantes?",
             "Existem evidências de coautorias ou projetos conjuntos com outros pesquisadores de destaque?", "O pesquisador já ocupou cargos administrativos relevantes (ex.: coordenador de programa de pós-graduação, diretor de instituto, etc.)?", "Ele lidera grupos de pesquisa reconhecidos pelo CNPq ou outras instituições?",
             "Há evidências de que os resultados das pesquisas do pesquisador geraram impacto social, tecnológico ou econômico?", "O pesquisador possui patentes ou outros produtos registrados oriundos de sua pesquisa?", "O pesquisador foi convidado como palestrante em eventos científicos de prestígio?", "Ele já recebeu prêmios ou reconhecimentos por sua contribuição científica?"
             ]



tags_relacionadas = []

for prompt in prompts_list:
    #categoriza o prompt
    tags_rel = extract_related_tags(prompt)
    #extrai as tags da categorização
    tags_alinhadas = extract_prompt_tags(tags_rel)

    tags_relacionadas.append([prompt,tags_alinhadas])
    
    
#armazena a quantidade de tokens necessario para responder cada pergunta para cada curriculo
qtd_curriculo_pergunta = []

#log para saber como estão os dados
log = ""

#para cada curriculo
for selected_resume in stored_resumes:
    # adiciona o nome do curriculo no log
    print(selected_resume)
    log += f"### curriculo: {selected_resume}\n"
    #processa o curriculo
    curriculo_processado = process_resume(os.path.join(CURRICULO_DIR, selected_resume))    
    #armazena a quantidade de tokens para cada pergunta em um curriculo
    qtd_tokens_curriculo = []
    
    #para cada conjunto pergunta/tags
    for conj in tags_relacionadas:
        
        #adiciona as perguntas e tags ao log
        log += f"# pergunta: {conj[0]}\n# tags: {conj[1]}\n"
        
        #retira as seções das tags do curriculo
        processed_data = extract_attributes_chatbot(conj[1], curriculo_processado)

        #ainda precisa somar com os prompts de mensagem para o sistema e prompt do usuario
        sys_message = """Aja como um avaliador de currículos acadêmicos que está procurando profissionais especializados em uma área específica, e
        decide avaliar de forma qualitativa se o profissional se enquadra no perfil procurado pelo seu instituto. Responda à consulta do usuário com
        base no conteúdo do currículo abaixo.\n
        ### DADOS ###  ### FIM DOS DADOS ###
        """
        
        #adiciona os dados ao log
        #log += f"# processed data: {processed_data.__str__()}\n"
        
        
        #dados completos, contendo mensagem do sistema, prompt do usuario e dados são unidos
        complete_data = sys_message + processed_data.__str__() + conj[0]
        
        #enconding do modelo
        encoding = tiktoken.encoding_for_model("gpt-4o-mini-2024-07-18")
        #faz os tokens
        tokens = encoding.encode(complete_data)
        #conta os tokens
        qtd_tokens = len(tokens)
        #adiciona a quantidade de tokens no armazenador
        qtd_tokens_curriculo.append(qtd_tokens)
        
        
        str = f"""Quantidade de tokens ao todo: {qtd_tokens}\n"""
        #print(str)
        
        #adiciona a quantidade de tokens no log
        log += f"#{str}"
        
        with open("log_analises.txt", "w", encoding="utf-8") as arquivo:
            arquivo.write(log)
    
    qtd_curriculo_pergunta.append(qtd_tokens_curriculo)
    
data_tokens = np.array(qtd_curriculo_pergunta)
np.save("data_tokens.npy", data_tokens)

        
    