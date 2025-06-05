import os
import sys
import streamlit as st
import json
import time
import tiktoken
import shutil
from datetime import datetime


# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.business_logic.query_handler import  final_response_generator_log, extract_attributes_chatbot, handle_query_chat, buscar_chave
#from app.api.openai_api import extract_related_tags
from app.business_logic.resume_processor import process_resume
from app.data_access.file_manager import list_curriculos
from app.api.openai_api import partial_request, final_request, prompt_categorizer, gpt_request, gemini_request
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



def processar_pastas(pasta_base):
    # Garante que o caminho seja absoluto
    pasta_base = os.path.abspath(pasta_base)

    # Itera por todos os itens na pasta base
    for nome_pasta in os.listdir(pasta_base):
        caminho_pasta = os.path.join(pasta_base, nome_pasta)

        # Verifica se é uma pasta
        if os.path.isdir(caminho_pasta):
            arquivos = os.listdir(caminho_pasta)

            # Verifica se há exatamente um arquivo na pasta
            if len(arquivos) == 1:
                nome_arquivo_original = arquivos[0]
                caminho_arquivo_original = os.path.join(caminho_pasta, nome_arquivo_original)

                # Define o novo nome com base no nome da pasta
                novo_nome_arquivo = nome_pasta + ".xml"
                novo_caminho_arquivo = os.path.join(pasta_base, novo_nome_arquivo)

                # Move e renomeia o arquivo para a pasta base
                shutil.move(caminho_arquivo_original, novo_caminho_arquivo)

                # Remove a pasta vazia
                os.rmdir(caminho_pasta)
            else:
                print(f"Pasta '{nome_pasta}' não contém exatamente um arquivo. Ignorada.")


def verifica_tamanho(pasta_base):
    # Define o codificador de tokens
    encoder = tiktoken.encoding_for_model("gpt-4o-mini-2024-07-18")
    # Garante que o caminho seja absoluto
    pasta_base = os.path.abspath(pasta_base)
    # Itera por todos os itens na pasta base
    for arquivo_nome in os.listdir(pasta_base):
        curriculo_processado = process_resume(os.path.join(pasta_base, arquivo_nome))
        str_curriculo = json.dumps(curriculo_processado)
        tokenized_curriculo = encoder.encode(str_curriculo)
        
        if(len(tokenized_curriculo)< 122000):
            print(arquivo_nome)
        log_1(f"Arquivo: {arquivo_nome}")
        log_1(f"Tamanho em tokens: {len(tokenized_curriculo)}\n")
        




prompt_list_3 = [
"A pesquisadora Marina Legroski possui alguma conta na rede social twitter/x, pesquise na internet"
]

# curriculo_processado = process_resume("/home/lucasdarcio/home/pibic_prim/PIBIC-Chatbot-App/curriculos/Altigran Soares da Silva.xml")
# str_curri = str(curriculo_processado)
# encoder = tiktoken.encoding_for_model("gpt-4o-mini-2024-07-18")
# encoded_curriculo = encoder.encode(str_curri)
# print(len(encoded_curriculo))

# Função auxiliar para registrar no log
def log_1(msg, file_name="Log_Chats.txt"):
    # Caminho fixo para o arquivo de log de debug
    log_path = os.path.join(os.getcwd(), file_name)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        
#"Tayana Uchoa Conte", 
curriculos = ["Marina Chiara Legroski"]

for c in curriculos:
    curriculo_processado = process_resume("/home/lucasdarcio/home/pibic_prim/PIBIC-Chatbot-App/curriculos/"+c+".xml")

    for i in prompt_list_3:
        while True:
            log_1(f"Prompt: {i}", file_name="gemini-"+c+".txt")
            try:
                print("resposta do gemini sendo processada")
                response = gemini_request(i, json.dumps(curriculo_processado))
                log_1(f"Resposta:\n{response}", file_name="gemini-"+c+".txt")
                print("respostas do gemini terminada")
                break

            except Exception as e:
                print("erro ao chamar o gemini")
                log_1(f"Erro ao chamar o Gemini: {e}", file_name="gemini-"+c+".txt")
            
            #time.sleep(210)
        
    for i in prompt_list_3:
        log_1(f"Prompt: {i}", file_name="arquitetura-"+c+".txt")
        print(f"Arquivo: {"arquitetura-"+c+".txt"} criado, começando o processamento da arquitetura")
        resp_arqu = final_response_generator_log(i, curriculo_processado, 122000, c)
        print(f"Processamento terminado")
        log_1(f"Respostas: {resp_arqu}", file_name="arquitetura-"+c+".txt")