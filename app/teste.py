import os
import sys
import streamlit as st
import json
import tiktoken

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

# função que retorna o valor da chave procurada
def buscar_chave(obj, chave_procurada):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == chave_procurada:
                return v
            resultado = buscar_chave(v, chave_procurada)
            if resultado is not None:
                return resultado
    elif isinstance(obj, list):
        for item in obj:
            resultado = buscar_chave(item, chave_procurada)
            if resultado is not None:
                return resultado
    return None

# função que recebe o prompt e retorna a resposta
def final_response_generator(prompt, dict_cv, max_context_request):
    # Categoriza a prompt
    categoria = categorizar_prompt(prompt)

    # Extrai tags associadas à categoria
    tags_relacionadas = extract_prompt_tags(categoria)

    # Inicializa o contexto do request
    context_request = {}

    # Armazena tudo que já foi usado
    all_context = {}

    # Armazena as respostas intermediárias
    responses = []

    # Codificador de tokens
    encoder = tiktoken.get_encoding("gpt-algum")

    for i, tag_rel in enumerate(tags_relacionadas):
        # Pula se a tag já foi usada em algum lugar do contexto
        if buscar_chave(all_context, tag_rel):
            continue

        # Recupera o conteúdo da tag
        content_tag_rel = dict_cv.get(tag_rel, "")

        # Calcula tokens atuais
        tam_ctxt_rqst = len(encoder.encode(json.dumps(context_request)))
        tam_tag_rel = len(encoder.encode(content_tag_rel))

        # Se estourar o limite, envia e reinicia o contexto
        if tam_ctxt_rqst + tam_tag_rel > max_context_request:
            context_string = json.dumps(context_request)
            responses.append(response_section_llm(context_string, prompt))
            context_request = {}

        # Adiciona a nova tag ao contexto atual e ao total
        context_request[tag_rel] = content_tag_rel
        all_context[tag_rel] = content_tag_rel

        # Última iteração → força envio
        if i == len(tags_relacionadas) - 1:
            context_string = json.dumps(context_request)
            responses.append(response_section_llm(context_string, prompt))

    # Junta as respostas parciais e envia para resumo final
    combined_responses = "\n\n".join(responses)
    final_response = response_final_llm(combined_responses, prompt)

    return final_response