import os
import sys
import streamlit as st
import json
import tiktoken

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.business_logic.query_handler import  final_response_generator_log, extract_attributes_chatbot, handle_query_chat, buscar_chave
#from app.api.openai_api import extract_related_tags
from app.business_logic.resume_processor import process_resume
from app.data_access.file_manager import list_curriculos
from app.api.openai_api import partial_request, final_request, prompt_categorizer
from app.business_logic.compression_utils import extract_prompt_tags

import json

def get_json_data_types(json_data, types_found=None):
    if types_found is None:
        types_found = set()

    if isinstance(json_data, dict):
        types_found.add('dict')
        for value in json_data.values():
            get_json_data_types(value, types_found)
    elif isinstance(json_data, list):
        types_found.add('list')
        for item in json_data:
            get_json_data_types(item, types_found)
    elif isinstance(json_data, str):
        types_found.add('str')
    elif isinstance(json_data, int):
        types_found.add('int')
    elif isinstance(json_data, float):
        types_found.add('float')
    elif isinstance(json_data, bool):
        types_found.add('bool')
    elif json_data is None:
        types_found.add('null')  # ou 'NoneType'
    else:
        types_found.add(type(json_data).__name__)  # tipo desconhecido

    return types_found

def get_types_from_json_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return list(get_json_data_types(data))


# Diretório onde os currículos armazenados ficam
CURRICULO_DIR = "curriculos/"



prompts_list_1 = [
            "Qual é a quantidade e a qualidade dos artigos publicados pelo pesquisador em periódicos indexados de alto impacto?",
            "As publicações estão concentradas em revistas ou conferências de relevância na área de atuação?",
            "Qual é o número de citações dos artigos do pesquisador em bases como Scopus ou Google Scholar?",
            "O pesquisador possui índice h (h-index) ou outros indicadores de impacto significativo na sua área?",
            "O pesquisador já liderou ou participou como proponente de projetos financiados por agências de fomento?",
            "Qual é o histórico do pesquisador em atrair recursos de pesquisa por meio de editais competitivos?",
            "Quantos alunos de mestrado, doutorado e iniciação científica o pesquisador já orientou ou está orientando?",
            "Qual é a relevância das produções acadêmicas desenvolvidas por seus orientandos, como publicações ou trabalhos apresentados?",
            "O pesquisador contribui para a formação de alunos na graduação por meio de atividades como orientação de TCC ou projetos de pesquisa?",
            "Qual é o impacto das orientações na carreira acadêmica ou profissional dos alunos formados?",
            "O pesquisador participa de redes de colaboração nacionais ou  internacionais relevantes?",
            "Existem evidências de coautorias ou projetos conjuntos com outros pesquisadores de destaque?",
            "O pesquisador já ocupou cargos administrativos relevantes (ex.: coordenador de programa de pós-graduação, diretor de instituto, etc.)?",
            "Ele lidera grupos de pesquisa reconhecidos pelo CNPq ou outras instituições?",
            "Há evidências de que os resultados das pesquisas do pesquisador geraram impacto social, tecnológico ou econômico?",
            "O pesquisador possui patentes ou outros produtos registrados oriundos de sua pesquisa?",
            "O pesquisador foi convidado como palestrante em eventos científicos de prestígio?",
            "Ele já recebeu prêmios ou reconhecimentos por sua contribuição científica?"
            ]

prompt_list_2 = [
            "Qual é a quantidade de artigos publicados pelo pesquisador em periódicos indexados, e quantos deles estão em periódicos classificados nos estratos A1 ou A2 da área pela plataforma Qualis?",
            "As publicações do pesquisador estão concentradas em revistas ou conferências indexadas em bases como Scopus, Web of Science ou classificadas nos níveis A1/A2 do Qualis da área?",
            "Quantas citações os artigos do pesquisador receberam em bases como Scopus, Web of Science ou Google Scholar, considerando também a média de citações por artigo?",
            "Qual é o valor do índice h (h-index) do pesquisador em bases como Scopus ou Google Scholar, e como ele se compara com a média de sua área de atuação?",
            "Quantos projetos de pesquisa com financiamento aprovado o pesquisador já coordenou ou participou como proponente, e quais foram as respectivas agências financiadoras (ex.: CNPq, Fapesp, CAPES)?",
            "Qual foi o valor total de recursos de pesquisa captados pelo pesquisador nos últimos cinco anos por meio de editais de agências públicas ou privadas?",
            "Quantos alunos de mestrado, doutorado e iniciação científica o pesquisador orientou e quantos desses já concluíram suas respectivas formações?",
            "Quantas publicações ou apresentações em eventos científicos foram realizadas por alunos orientados pelo pesquisador, e quantas dessas ocorreram em eventos ou periódicos indexados?",
            "O pesquisador orientou quantos trabalhos de conclusão de curso (TCC) ou projetos de pesquisa de graduação nos últimos cinco anos?",
            "Quantos dos alunos orientados pelo pesquisador seguiram carreira acadêmica (ex.: ingresso em pós-graduação) ou foram empregados em áreas relacionadas à sua formação?",
            "Em quantas redes de colaboração científica nacionais ou internacionais o pesquisador participa formalmente, como projetos interinstitucionais ou consórcios de pesquisa?",
            "Quantos artigos ou projetos o pesquisador desenvolveu em coautoria com docentes ou pesquisadores de outras instituições, e quantos desses coautores possuem produtividade reconhecida (ex.: bolsa PQ do CNPq ou produção qualificada)?",
            "Quais cargos administrativos o pesquisador já ocupou, como coordenação de curso, chefia de departamento, direção de unidade acadêmica ou coordenação de programa de pós-graduação stricto sensu?",
            "O pesquisador lidera grupos de pesquisa certificados pelo CNPq, e com quantos membros ativos esse grupo conta atualmente?",
            "Há registros documentados (ex.: relatórios, notícias, parcerias institucionais) de que os resultados das pesquisas do pesquisador foram utilizados em políticas públicas, desenvolvimento tecnológico ou ações sociais?",
            "Quantos registros de patentes, softwares, protótipos, cultivares ou outros produtos tecnológicos o pesquisador possui junto ao INPI, SUFRAMA ou outras instituições oficiais?",
            "Quantas vezes o pesquisador foi convidado como palestrante ou conferencista em eventos científicos nacionais ou internacionais com processo seletivo ou curadoria institucional?",
            "Quantos prêmios, menções honrosas ou títulos o pesquisador recebeu por sua atuação científica, técnica ou acadêmica, e quais instituições concederam tais reconhecimentos?"
]



curriculo_name = "Alba Cristina Magalhães Alves de Melo.xml"
curriculo_processado = process_resume(os.path.join(CURRICULO_DIR, curriculo_name))   


for i in prompt_list_2:
    final_response_generator_log(i, curriculo_processado, 122000, curriculo_name)
    


#for i in prompts_list :
    #final_response_generator_log(i, curriculo_processado, 122000, curriculo_name)