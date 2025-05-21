import json
import tiktoken
import os
from datetime import datetime
from app.api.openai_api import partial_request, final_request, prompt_categorizer
from app.business_logic.compression_utils import extract_tags

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


def final_response_generator(prompt, dict_cv, max_context_request):
    # Detecta a categoria do prompt
    categoria = prompt_categorizer(prompt)

    # Extrai tags relacionadas à categoria
    tags_relacionadas = extract_tags(categoria)

    # Define o codificador de tokens
    encoder = tiktoken.encoding_for_model("gpt-4o-mini-2024-07-18")

    context_request = ""
    responses = []

    for i, tag_rel in enumerate(tags_relacionadas):
        
        # Busca o conteúdo associado à tag
        content_tag_rel = buscar_chave(dict_cv, tag_rel)
        if content_tag_rel is None:
            continue  # Pula caso não encontre a tag no dicionário
        
        # conteudo da tag em string
        str_content_tag = str(content_tag_rel)
        
        # Codifica a string para contar os tokens
        content_tag_encoded = encoder.encode(str_content_tag)
        tokens_tag = len(content_tag_encoded)
        
        #encoded do context_request
        context_request_encoded = encoder.encode(context_request)
        tokens_antes = len(context_request_encoded)


        # Trunca uma tag se ela sozinha é maior que o contexto
        while(tokens_tag >= max_context_request):
            # verica quanto falta para o context_request para ter o tamanho maximo
            left = max_context_request-tokens_tag
            
            # separa o encoded da tag nova
            first_part_encoded = content_tag_encoded[:left - 10]
            second_part_encoded = content_tag_encoded[left - 10:]
            
            # Adiciona a primeira parte para o que resta de espaço no context_request e envia a request
            first_part_decoded = encoder.decode(first_part_encoded)
            context_request+=first_part_decoded
            resposta = partial_request(prompt, context_request)
            responses.append(resposta)
            context_request = ""
            
            # A segunda parte se torna o conteudo da tag inteira para verificar se ainda é grande demais
            content_tag_encoded = second_part_encoded
            str_content_tag = encoder.decode(content_tag_encoded)
            tokens_tag = len(content_tag_encoded)
            
            # refaz o encoded do context_request
            context_request_encoded = encoder.encode(context_request)
            tokens_antes = len(context_request_encoded)
            

        # Se as tags acumulado mais a nova tag excederem o limite, faz uma requisição parcial com o acumulado, se não adiciona a nova tag as tags acumulada
        if tokens_antes + tokens_tag > max_context_request and context_request != "":
            resposta = partial_request(prompt, context_request)
            responses.append(resposta)
            context_request = ""
            

        # Adiciona o conteúdo da tag ao contexto acumulado
        context_request += str_content_tag

        # Se for a última tag e houver contexto restante, faz a última requisição parcial
        if i == len(tags_relacionadas) - 1 and context_request != "":
            resposta = partial_request(prompt, context_request)
            responses.append(resposta)

    # Combina todas as respostas parciais
    combined_responses = "\n\n".join(responses)

    # Gera a resposta final com base nas respostas parciais combinadas
    final_response = final_request(combined_responses, prompt)

    return final_response


# Função auxiliar para registrar no log
def log(msg):
    # Caminho fixo para o arquivo de log de debug
    log_path = os.path.join(os.getcwd(), "debug_log_02.txt")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")


def final_response_generator_log(prompt, dict_cv, max_context_request, curriculo_name):

    prompt = "nome de arquivo do curriculo: "+curriculo_name+"\nprompt: \n"+prompt
    log("\n================ INÍCIO DA EXECUÇÃO ================\n")
    log(f"Prompt recebido: {prompt}")
    log(f"Contexto máximo permitido (tokens): {max_context_request}")
    
    # Detecta a categoria do prompt
    categoria = prompt_categorizer(prompt)
    log(f"Categoria detectada: {categoria}")

    # Extrai tags relacionadas à categoria
    tags_relacionadas = extract_tags(categoria)
    log(f"Tags relacionadas extraídas: {tags_relacionadas}")

    # Define o codificador de tokens
    encoder = tiktoken.encoding_for_model("gpt-4o-mini-2024-07-18")

    context_request = ""
    responses = []

    for i, tag_rel in enumerate(tags_relacionadas):
        log(f"\n--- Processando tag [{i+1}/{len(tags_relacionadas)}]: {tag_rel} ---")
        
        # Busca o conteúdo associado à tag
        content_tag_rel = buscar_chave(dict_cv, tag_rel)
        if content_tag_rel is None:
            log(f"Tag não encontrada, Pulando")
            if i == len(tags_relacionadas) - 1 and context_request != "":
                log(f"É a ultima tag da lista  e o contexto não está vazio, então envia para partial request")
                resposta = partial_request(prompt, context_request)
                responses.append(resposta)
            
            continue  # Pula caso não encontre a tag no dicionário
        
        # conteudo da tag em string
        str_content_tag = str(content_tag_rel)
        
        #encoded do context_request
        context_request_encoded = encoder.encode(context_request)
        tokens_antes = len(context_request_encoded)
        log(f"Tokens no contexto atual: {tokens_antes}")
        
        
        # Codifica a string para contar os tokens
        content_tag_encoded = encoder.encode(str_content_tag)
        tokens_tag = len(content_tag_encoded)
        log(f"Tokens do conteudo da tag extraido: {tokens_tag}")
        


        # Trunca uma tag se ela sozinha é maior que o contexto
        while(tokens_tag >= max_context_request):
            log(f"Tokens da tag maior que o maximo de contexto, Trunca ela")
            # verica quanto falta para o context_request para ter o tamanho maximo
            left = max_context_request - tokens_antes
            log(f"Espaço restante no contexto: {left}")
            
            # separa o encoded da tag nova
            first_part_encoded = content_tag_encoded[:left - 10]
            log(f"Tamanho no first_part_encoded: {len(first_part_encoded)}")
            
            second_part_encoded = content_tag_encoded[left - 10:]
            log(f"Tamanho no second_part_encoded: {len(second_part_encoded)}")
            
            
            
            # Adiciona a primeira parte para o que resta de espaço no context_request e envia a request
            first_part_decoded = encoder.decode(first_part_encoded)
            context_request+=first_part_decoded
            log(f"Tamanho no contexto apos adicionar a parte inicial da seção truncada: {len(encoder.encode(context_request))}")
            
            resposta = partial_request(prompt, context_request)
            responses.append(resposta)
            
            log(f"primeira seção da tag adicionada no contexto e enviada ao partial request")
            context_request = ""
            
            # A segunda parte se torna o conteudo da tag inteira para verificar se ainda é grande demais
            content_tag_encoded = second_part_encoded
            str_content_tag = encoder.decode(content_tag_encoded)
            tokens_tag = len(content_tag_encoded)
            
            
            # refaz o encoded do context_request
            context_request_encoded = encoder.encode(context_request)
            tokens_antes = len(context_request_encoded)
            
        log(f"A segunda seção da tag sera tratada como a tag completa agora")

        # Se as tags acumulado mais a nova tag excederem o limite, faz uma requisição parcial com o acumulado, se não adiciona a nova tag as tags acumulada
        if tokens_antes + tokens_tag > max_context_request and context_request != "":
            log(f"A quantidade de token no contexto + tag é maior que o maximo e o contexto não está vazio")
            
            resposta = partial_request(prompt, context_request)
            log(f"Request enviada para o partial request")
            
            responses.append(resposta)
            context_request = ""
            

        # Adiciona o conteúdo da tag ao contexto acumulado
        context_request += str_content_tag
        log(f"Conteudo da tag adicionado ao contexto")

        # Se for a última tag e houver contexto restante, faz a última requisição parcial
        if i == len(tags_relacionadas) - 1 and context_request != "":
            log(f"É a ultima tag da lista  e o contexto não está vazio, então envia para partial request")
            resposta = partial_request(prompt, context_request)
            responses.append(resposta)

    log(f"RESPOSTAS PARCIAIS:")
    for i, resposta in enumerate(responses):
        log(f"==Resposta {i+1} :\n {resposta}")
        
    # Combina todas as respostas parciais
    combined_responses = "\n\n".join(responses)
    
    log("COMBINED RESPONSE")
    log(combined_responses)

    # Gera a resposta final com base nas respostas parciais combinadas
    log(f"Request final:")
    final_response = final_request(combined_responses, prompt)
    log("🎯 RESPOSTA FINAL:")
    log(final_response)
    log("\n================ FIM DA EXECUÇÃO ================\n")

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
