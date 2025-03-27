import json
from app.api.openai_api import send_query_to_openai_chat_bot


def buscar_chave(dados, chave):
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
            mini_analysis = send_query_to_openai_chat_bot(mini_context, f"{intermediary_query}")

            intermediary_analyses.append(mini_analysis)
        
    else:
        intermediary_analyses = [send_query_to_openai_chat_bot(context, f"{intermediary_query}")]
        
    intermediary_analyses = "\n\n".join(intermediary_analyses)


    response = send_query_to_openai_chat_bot(intermediary_analyses, f"{query}")
    # response = None
    return response, intermediary_analyses

