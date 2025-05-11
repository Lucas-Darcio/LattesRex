import json
import tiktoken
from datetime import datetime
from app.api.openai_api import partial_request, final_request, prompt_categorizer
from app.business_logic.compression_utils import extract_prompt_tags

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
    categoria = prompt_categorizer(prompt)

    # Extrai tags associadas à categoria
    tags_relacionadas = extract_prompt_tags(categoria)

    # Inicializa o contexto do request
    context_request = {}

    # Armazena tudo que já foi usado
    all_context = {}

    # Armazena as respostas intermediárias
    responses = []

    # Codificador de tokens
    encoder = tiktoken.get_encoding("gpt-4o-mini-2024-07-18")

    for i, tag_rel in enumerate(tags_relacionadas):
        # Pula se a tag já foi usada em algum lugar do contexto
        if buscar_chave(all_context, tag_rel):
            continue

        # Recupera o conteúdo da tag
        content_tag_rel = dict_cv.get(tag_rel, "")
        
        # transforma os dicts em strings
        str_context_request = json.dumps(context_request)
        str_content_tag = json.dumps(content_tag_rel)
        
        # encoding da string
        encoded_content_tag = encoder.encode(str_content_tag)

        # Calcula tokens atuais
        tam_content_tag = len(encoded_content_tag)

        ### Para verificar o tamanho total de tokens faço adiciono a tag no context request
        # faz uma copia de context_request
        context_request_test = context_request.copy()
        # adiciona a tag na compia de context request
        context_request_test[tag_rel] = content_tag_rel
        # transifrma em string
        str_test = json.dumps(context_request_test)
        # verifica o tamanho de tokens final
        tam_test = len(encoder.encode(str_test))

        if tam_test > max_context_request:
            responses.append(partial_request(prompt, categoria, str_context_request))
            context_request = {}

        # Se a tag sozinha for maior que o maximo de contexto
        if (tam_content_tag > max_context_request):
            encoded_content_tag = encoded_content_tag[-(max_context_request-2):]
            str_content_tag = encoder.decode(encoded_content_tag)
            content_tag_rel = json.loads(str_content_tag)

        # Adiciona a nova tag ao contexto atual e ao total
        context_request[tag_rel] = content_tag_rel
        all_context[tag_rel] = content_tag_rel

        # Última iteração → força envio
        if i == len(tags_relacionadas) - 1:
            context_string = json.dumps(context_request)
            responses.append(partial_request(prompt, categoria, context_string))

    # Junta as respostas parciais e envia para resumo final
    combined_responses = "\n\n".join(responses)
    final_response = final_request(combined_responses, prompt)

    return final_response


def final_response_generator_log(prompt, dict_cv, max_context_request):
    # Inicializa log
    with open("debug_log.txt", "a", encoding="utf-8") as log:
        log.write(f"\n{'='*60}\n")
        log.write(f"Execução em {datetime.now()}\n")
        log.write(f"Prompt: {prompt}\n")

    # Categoriza a prompt
    categoria = prompt_categorizer(prompt)

    with open("debug_log.txt", "a", encoding="utf-8") as log:
        log.write(f"Categoria: {categoria}\n")

    # Extrai tags associadas à categoria
    tags_relacionadas = extract_prompt_tags(categoria)

    with open("debug_log.txt", "a", encoding="utf-8") as log:
        log.write(f"Tags relacionadas: {tags_relacionadas}\n")

    # Inicializa o contexto do request
    context_request = {}

    # Armazena tudo que já foi usado
    all_context = {}

    # Armazena as respostas intermediárias
    responses = []

    # Codificador de tokens
    encoder = tiktoken.get_encoding("gpt-4o-mini")

    for i, tag_rel in enumerate(tags_relacionadas):
        tag_info = f"\n[Tag {i+1}/{len(tags_relacionadas)}: {tag_rel}]\n"
        
        # Pula se a tag já foi usada em algum lugar do contexto
        if buscar_chave(all_context, tag_rel):
            tag_info += f"→ Tag '{tag_rel}' pulada (já usada)\n"
            with open("debug_log.txt", "a", encoding="utf-8") as log:
                log.write(tag_info)
            continue

        # Recupera o conteúdo da tag
        content_tag_rel = dict_cv.get(tag_rel, "")
        
        # transforma os dicts em strings
        str_context_request = json.dumps(context_request)
        str_content_tag = json.dumps(content_tag_rel)
        
        # encoding da string
        encoded_content_tag = encoder.encode(str_content_tag)

        # Calcula tokens atuais
        tam_content_tag = len(encoded_content_tag)

        # Verifica o tamanho de context_request + nova tag
        context_request_test = context_request.copy()
        context_request_test[tag_rel] = content_tag_rel
        str_test = json.dumps(context_request_test)
        tam_test = len(encoder.encode(str_test))

        # Adiciona dados ao log
        tag_info += f"Tamanho da tag isolada: {tam_content_tag} tokens\n"
        tag_info += f"Tamanho do contexto teste (com a tag): {tam_test} tokens\n"
        tag_info += f"Excede max_context_request? {tam_test > max_context_request}\n"
        tag_info += f"Tag sozinha excede limite? {tam_content_tag > max_context_request}\n"

        with open("debug_log.txt", "a", encoding="utf-8") as log:
            log.write(tag_info)

        # Se tamanho total com a tag exceder o limite
        if tam_test > max_context_request:
            responses.append(partial_request(prompt, categoria, str_context_request))
            context_request = {}

        # Se a tag sozinha for maior que o maximo de contexto
        if tam_content_tag > max_context_request:
            encoded_content_tag = encoded_content_tag[-(max_context_request-2):]
            str_content_tag = encoder.decode(encoded_content_tag)
            try:
                content_tag_rel = json.loads(str_content_tag)
            except json.JSONDecodeError:
                with open("debug_log.txt", "a", encoding="utf-8") as log:
                    log.write("❗ Erro ao decodificar JSON truncado da tag. Tag ignorada.\n")
                continue

        # Adiciona a nova tag ao contexto atual e ao total
        context_request[tag_rel] = content_tag_rel
        all_context[tag_rel] = content_tag_rel

        # Última iteração → força envio
        if i == len(tags_relacionadas) - 1:
            context_string = json.dumps(context_request)
            responses.append(partial_request(prompt, categoria, context_string))

    # Junta as respostas parciais e envia para resumo final
    combined_responses = "\n\n".join(responses)
    final_response = final_request(combined_responses, prompt)

    with open("debug_log.txt", "a", encoding="utf-8") as log:
        log.write(f"\nResposta final combinada:\n{final_response}\n")
        log.write(f"{'='*60}\n")

    return final_response



def extract_attributes_chatbot(tags, curriculo):
    
    result = {}

    for tag in tags:
        print(tag)

        valor = buscar_chave(curriculo, tag)
        
        if tag in result:
            result[tag].append(valor)
        else:
            result[tag] = [valor]

    return result

 


def handle_query_chat(curriculo_data, query):
    # Gera o contexto para o LLM a partir do currículo processado
    # evaluation_metric = "Conclua sua análise com uma das seguintes notas: \n1-Muito fraco; 2-Fraco; 3-Médio; 4-Bom; 5-Muito bom. \nApós isso, explique seu raciocínio em passo a passo." #"### start of output format ###\n Conclua sua análise com apenas um dos seguintes valores: \n1-Muito fraco; 2-Fraco; 3-Médio; 4-Bom; 5-Muito bom.\nVamos pensar por passo a passo..\n### end of output format ###"
    # response_format = query['response_format']

    # context = extract_attributes(query, curriculo_data) # extração de só as tags importantes do curriculo_data

    # Send context in batches
    
    context = curriculo_data.__str__()
    char_per_batch = 128000
    intermediary_query = query

    intermediary_analyses = []
    
    if len(context) > char_per_batch:
        for i in range(0, len(context) - char_per_batch, char_per_batch):
            end = char_per_batch if i + char_per_batch <= len(context) else len(context)
            mini_context = context[i : i + end]
            print(f"mini analise: {i} enviada\n")
            #mini_analysis = send_query_to_openai_chat_bot(mini_context, f"{intermediary_query}")

            #intermediary_analyses.append(mini_analysis)
        
    #else:
        #intermediary_analyses = [send_query_to_openai_chat_bot(context, f"{intermediary_query}")]
        
    #intermediary_analyses = "\n\n".join(intermediary_analyses)


    #response = send_query_to_openai_chat_bot(intermediary_analyses, f"{query}")
    # response = None
    #return response, intermediary_analyses

def old_buscar_chave(dados, chave):
    """
    Busca recursivamente por uma chave em um JSON aninhado e retorna o primeiro valor encontrado.

    :param dados: Dicionário ou lista contendo os dados JSON.
    :param chave: String representando a chave a ser buscada (exemplo: "#ATUACOES-PROFISSIONAIS").
    :return: O primeiro valor encontrado para a chave ou None se não for encontrado.
    """
    chave = chave.lstrip("#")  # Remove o "#" do início da chave

    if isinstance(dados, dict):
        if chave in dados:
            return dados[chave]
        for valor in dados.values():
            resultado = buscar_chave(valor, chave)
            if resultado is not None:
                return resultado

    elif isinstance(dados, list):
        for item in dados:
            resultado = buscar_chave(item, chave)
            if resultado is not None:
                return resultado

    return None
