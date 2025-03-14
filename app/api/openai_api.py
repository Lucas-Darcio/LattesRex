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
            {"role": "system", "content": system},
            {"role": "user", "content": query}
        ]
    )
    
    return completion.choices[0].message.content


