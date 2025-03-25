import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis de ambiente
    
def send_query_to_openai_chat_bot(context, query):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    system = f"Aja como um avaliador de currículos acadêmicos que está procurando profissionais especializados em uma área específica, e decide avaliar de forma qualitativa se o profissional se enquadra no perfil procurado pelo seu instituto. Responda à consulta do usuário com base no conteúdo do currículo abaixo.\n"
    system += f"### DADOS ### {context} ### FIM DOS DADOS ###"
    
    
    completion = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18", 
        messages= [
            {"role": "developer", "content": system},
            {"role": "user", "content": query}
        ]
    )
    
    return completion.choices[0].message.content



def extract_related_tags(user_input):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    system = f"Você é um assistente que aje como um classificador, e dado a seguinte lista de tags, analise o prompt do usuário e retorne as tags que mais se alinham com a requisição do prompt"
    system += f"### LISTA DE TAGS ### #ATUACOES-PROFISSIONAIS #FORMACAO-ACADEMICA-TITULACAO #AREAS-DE-ATUACAO #PREMIOS-TITULOS #PRODUCAO-BIBLIOGRAFICA #TRABALHOS-EM-EVENTOS #ARTIGOS-PUBLICADOS #PRODUCAO-TECNICA #ORIENTACOES-CONCLUIDAS #OUTRA-PRODUCAO ### FIM DA LISTA DE TAGS ###"
    
    
    completion = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18", 
        messages= [
            {"role": "developer", "content": system},
            {"role": "user", "content": f"Prompt a ser analisado: {user_input}"}
        ]
    )
    
    return completion.choices[0].message.content
   