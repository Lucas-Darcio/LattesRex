import os
import sys
import tiktoken

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.api.openai_api import extract_related_tags
from app.data_access.file_manager import list_curriculos, load_curriculo
from app.business_logic.resume_processor import process_resume

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

for user_input in prompts_list:
    
    tags_rel = extract_related_tags(user_input)
    tags_relacionadas.append([user_input,tags_rel])

for selected_resume in stored_resumes:
    curriculo_data = process_resume(os.path.join(CURRICULO_DIR, selected_resume))

    
    