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
        tokens_antes = len(encoder.encode(context_request))

        # Busca o conteúdo associado à tag
        content_tag_rel = buscar_chave(dict_cv, tag_rel)
        if content_tag_rel is None:
            continue  # Pula caso não encontre a tag no dicionário

        str_content_tag = str(content_tag_rel)

        # Codifica a string para contar os tokens
        content_tag_encoded = encoder.encode(str_content_tag)
        tokens_tag = len(content_tag_encoded)

        # Trunca o conteúdo se exceder o limite
        if tokens_tag > max_context_request:
            content_tag_encoded = content_tag_encoded[:max_context_request - 10]
            str_content_tag = encoder.decode(content_tag_encoded)

        # Se o contexto acumulado mais o novo conteúdo excederem o limite, faz uma requisição parcial
        if tokens_antes + tokens_tag > max_context_request and context_request != "":
            resposta = partial_request(prompt, categoria, context_request)
            responses.append(resposta)
            context_request = ""

        # Adiciona o conteúdo da tag ao contexto
        context_request += str_content_tag

        # Se for a última tag e houver contexto restante, faz a última requisição parcial
        if i == len(tags_relacionadas) - 1 and context_request != "":
            resposta = partial_request(prompt, categoria, context_request)
            responses.append(resposta)

    # Combina todas as respostas parciais
    combined_responses = "\n\n".join(responses)

    # Gera a resposta final com base nas respostas parciais combinadas
    final_response = final_request(combined_responses, prompt)

    return final_response


def final_response_generator_debug(prompt, dict_cv, max_context_request):
    # Caminho fixo para o arquivo de log de debug
    log_path = os.path.join(os.getcwd(), "debug_log.txt")

    # Função auxiliar para registrar no log
    def log(msg):
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")

    try:
        # Início do log
        log("\n================ INÍCIO DA EXECUÇÃO ================\n")
        log(f"Prompt recebido: {prompt}")
        log(f"Contexto máximo permitido (tokens): {max_context_request}")

        categoria = prompt_categorizer(prompt)
        log(f"Categoria detectada: {categoria}")

        tags_relacionadas = extract_tags(categoria)
        log(f"Tags relacionadas extraídas: {tags_relacionadas}")

        encoder = tiktoken.encoding_for_model("gpt-4o-mini-2024-07-18")
        context_request = ""
        responses = []

        for i, tag_rel in enumerate(tags_relacionadas):
            log(f"\n--- Processando tag [{i+1}/{len(tags_relacionadas)}]: {tag_rel} ---")
            tokens_antes = len(encoder.encode(context_request))
            log(f"Tokens antes de adicionar a tag: {tokens_antes}")

            content_tag_rel = buscar_chave(dict_cv, tag_rel)
            if content_tag_rel is None:
                log("⚠️ Conteúdo não encontrado para a tag. Pulando.")
                continue

            str_content_tag = str(content_tag_rel)
            content_tag_encoded = encoder.encode(str_content_tag)
            tokens_tag_original = len(content_tag_encoded)
            log(f"Tokens da tag original: {tokens_tag_original}")

            # Truncamento, se necessário
            if tokens_tag_original > max_context_request:
                content_tag_encoded = content_tag_encoded[:max_context_request - 10]
                str_content_tag = encoder.decode(content_tag_encoded)
                log(f"⚠️ Conteúdo da tag truncado para {len(content_tag_encoded)} tokens")

            tokens_tag_final = len(content_tag_encoded)
            log(f"Tokens da tag após tratamento: {tokens_tag_final}")

            # Envio de requisição parcial se extrapolar o limite
            if tokens_antes + tokens_tag_final > max_context_request and context_request != "":
                log("💬 Contexto acumulado extrapola limite. Enviando requisição parcial.")
                resposta = partial_request(prompt, categoria, context_request)
                responses.append(resposta)
                log(f"Resposta parcial registrada:\n{resposta}\n")
                context_request = ""

            # Acumula o conteúdo da tag no contexto
            context_request += str_content_tag

            # Última tag: enviar contexto restante
            if i == len(tags_relacionadas) - 1 and context_request != "":
                log("🚀 Última tag. Enviando contexto restante.")
                resposta = partial_request(prompt, categoria, context_request)
                responses.append(resposta)
                log(f"Resposta parcial final registrada:\n{resposta}\n")

        combined_responses = "\n\n".join(responses)
        log("✅ Requisições parciais combinadas. Enviando para resumo final.")

        final_response = final_request(combined_responses, prompt)
        log("🎯 Resumo final gerado:")
        log(final_response)
        log("\n================ FIM DA EXECUÇÃO ================\n")

        return final_response

    except Exception as e:
        log(f"❌ Erro inesperado: {str(e)}")
        raise  # propaga o erro após logar




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
