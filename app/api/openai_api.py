import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis de ambiente
    

def partial_request(prompt: str, categoria: str, context: str):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    system = f"""
Você é um assistente especializado na análise de currículos acadêmicos.

Está participando de um processo de análise de um currículo extenso demais para ser processado integralmente. Por isso, o currículo será fornecido em partes (seções), e você deverá contribuir com análises parciais que, posteriormente, serão combinadas para formar uma resposta final.

Para isso, você receberá três informações:
1. O prompt original enviado pelo usuário (que expressa o que ele deseja saber).
2. A categoria temática do prompt, previamente classificada com base em uma hierarquia de categorias acadêmicas.
3. Um trecho do currículo acadêmico (seção).

Sua tarefa é:
- Analisar o trecho do currículo levando em consideração o prompt e a categoria informada.
- Responder com base apenas nas informações que estão explícitas ou fortemente implícitas nesse trecho.
- Ignorar informações que não sejam pertinentes ao prompt.
- Não extrapolar para além do conteúdo disponível na seção fornecida.

Caso o trecho não contenha dados relevantes à pergunta do usuário, retorne uma resposta como:  
“Não há informações suficientes neste trecho para responder ao prompt do usuário.”

Apresente sua análise de forma clara, objetiva e bem estruturada.

---  

## Prompt do Usuário ##
{prompt}

## Categoria do Prompt ##
{categoria}

## Trecho do Currículo ##
{context}
---
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        max_tokens=3000,
        messages=[
            {"role": "developer", "content": system}
        ]
    )
    return completion.choices[0].message.content


def final_request(prompt: str, respostas: str):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    system = f"""
Você é um assistente especializado na análise de currículos acadêmicos.

Você receberá um conjunto de respostas parciais. Cada uma foi gerada a partir de uma análise de trecho específico do currículo de um acadêmico. Todas as análises seguem o mesmo prompt original, enviado por um usuário que deseja obter informações sobre o currículo.

Sua tarefa é gerar uma resposta única, clara, precisa e bem estruturada que atenda completamente ao prompt do usuário, utilizando apenas as informações fornecidas nas respostas parciais.

Instruções:

- Leia com atenção todas as respostas parciais fornecidas.
- Consolide as informações relevantes, eliminando repetições e redundâncias.
- Respeite o conteúdo: não invente ou assuma nada que não esteja explícito nas respostas parciais.
- Se houver contradições ou ambiguidade, destaque com cautela.
- A resposta final deve ser coerente, fluida e adequada ao nível de detalhe e linguagem esperados em uma análise acadêmica.
- Caso as respostas parciais sejam insuficientes, você pode incluir uma observação final indicando a limitação.

---

🔹 Prompt original do usuário:
{prompt}

🔹 Respostas parciais:
{respostas}
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        max_tokens=3000,
        messages=[
            {"role": "developer", "content": system}
        ]
    )
    return completion.choices[0].message.content


def prompt_categorizer(user_input: str):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    system = """
Você é um classificador inteligente de entradas textuais segundo categorias acadêmicas. Dada uma entrada de texto (prompt do usuário), sua tarefa é identificar a categoria mais apropriada entre uma lista de categorias.

Cada categoria representa um conjunto específico de informações dentro de um currículo acadêmico. Analise cuidadosamente o conteúdo, propósito e foco da entrada para decidir 
em qual categoria ela se encaixa melhor.

### Lista de categorias ###

1. **Identificação Pessoal e Profissional**  
   **Significado:**  
   Reúne informações básicas e de contato do acadêmico, como nome completo, CPF, data de nascimento, nacionalidade, endereço, e-mail institucional, telefone, e também vínculos institucionais e cargos ocupados.  
   **Tags associadas:**  
   ["#DADOS-GERAIS","#RESUMO-CV", "#ENDERECO", "#ENDERECO-PROFISSIONAL", "#ENDERECO-RESIDENCIAL", "#VINCULOS", "#OUTRAS-INFORMACOES-RELEVANTES", "#OUTROS", "#IDIOMAS"]

2. **Áreas de Atuação e Conhecimento**  
    **Significado:**  
    Define os campos científicos, tecnológicos ou artísticos nos quais o profissional atua, baseando-se em classificações como a da CAPES ou do CNPq.
    **Tags associadas:**
    ["#AREAS-DO-CONHECIMENTO", "#AREA-DO-CONHECIMENTO-1", "#AREA-DO-CONHECIMENTO-2", "#AREA-DO-CONHECIMENTO-3", "#SETORES-DE-ATIVIDADE", "#AREAS-DE-ATUACAO", "#AREA-DE-ATUACAO", "#PALAVRAS-CHAVE"]
    
3. **Formação Acadêmica e Qualificações**  
    **Significado:**  
    Descreve a trajetória educacional formal do profissional, incluindo cursos de graduação, pós-graduação (mestrado, doutorado), prêmios, especializações e outros certificados relevantes.  
    **Tags associadas:**
    ["#FORMACAO-ACADEMICA-TITULACAO", "#CURSO-TECNICO-PROFISSIONALIZANTE", "#ENSINO-FUNDAMENTAL-PRIMEIRO-GRAU", "#ENSINO-MEDIO-SEGUNDO-GRAU", "#GRADUACAO", "#APERFEICOAMENTO", "#ESPECIALIZACAO", "#MESTRADO", "#MESTRADO-PROFISSIONALIZANTE", "#DOUTORADO", "#RESIDENCIA-MEDICA", "#LIVRE-DOCENCIA", "#POS-DOUTORADO", "#FORMACAO-COMPLEMENTAR", "#FORMACAO-COMPLEMENTAR-DE-EXTENSAO-UNIVERSITARIA", "#MBA", "#FORMACAO-COMPLEMENTAR-CURSO-DE-CURTA-DURACAO", "#PREMIOS-TITULOS", "#PREMIO-TITULO"]
    
4. **Pesquisa e Projetos Acadêmicos**  
    **Significado:**  
    Abarca a participação e coordenação em projetos de pesquisa, linhas de pesquisa, bolsas recebidas, grupos de pesquisa e financiamento acadêmico.  
    **Tags associadas:**
    ["#LINHA-DE-PESQUISA", "#PROJETO-DE-PESQUISA", "#EQUIPE-DO-PROJETO", "#INTEGRANTES-DO-PROJETO", "#FINANCIADORES-DO-PROJETO", "#FINANCIADOR-DO-PROJETO", "#PRODUCOES-CT-DO-PROJETO", "#PRODUCAO-CT-DO-PROJETO", "#ATIVIDADES-DE-PESQUISA-E-DESENVOLVIMENTO", "#PESQUISA-E-DESENVOLVIMENTO", "#RELATORIO-DE-PESQUISA","#DEMAIS-TRABALHOS"]
    
5. **Orientações e Treinamentos**  
    **Significado:**  
    Diz respeito à atuação como orientador ou supervisor de estudantes, abrangendo orientações de TCC, iniciação científica, mestrado, doutorado e pós-doutorado, além de estágios e treinamentos supervisionados.  
    **Tags associadas:**
    ["#ORIENTACOES", "#TREINAMENTO", "#ORIENTACOES-CONCLUIDAS", "#ORIENTACOES-CONCLUIDAS-PARA-MESTRADO", "#ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO", "#ORIENTACOES-CONCLUIDAS-PARA-POS-DOUTORADO", "#OUTRAS-ORIENTACOES-CONCLUIDAS", "#ORIENTACOES-EM-ANDAMENTO",, "#OUTRAS-ORIENTACOES-EM-ANDAMENTO", "#PARTICIPACAO-EM-BANCA-TRABALHOS-CONCLUSAO", "#PARTICIPACAO-EM-BANCA-DE-MESTRADO", "#PARTICIPACAO-EM-BANCA-DE-DOUTORADO", "#PARTICIPACAO-EM-BANCA-DE-EXAME-QUALIFICACAO", "#PARTICIPACAO-EM-BANCA-DE-APERFEICOAMENTO-ESPECIALIZACAO", "#PARTICIPACAO-EM-BANCA-DE-GRADUACAO", "#OUTRAS-PARTICIPACOES-EM-BANCA"]
    
6. **Experiência Profissional**  
    **Significado:**  
    Inclui experiências em instituições públicas ou privadas, tanto no ensino quanto fora dele, como consultorias, empresas, atuação clínica, entre outras atividades profissionais.  
    **Tags associadas:**
    
    ["#ATUACOES-PROFISSIONAIS", "#ATUACAO-PROFISSIONAL", "#ATIVIDADES-DE-CONSELHO-COMISSAO-E-CONSULTORIA", "#CONSELHO-COMISSAO-E-CONSULTORIA", "#ATIVIDADES-DE-SERVICO-TECNICO-ESPECIALIZADO", "#SERVICO-TECNICO-ESPECIALIZADO"]
    
7. **Atividades Acadêmicas e Administrativas**  
    **Significado:**  
    Refere-se à participação em comissões, coordenações de cursos, chefias de departamento, organização de eventos, entre outras responsabilidades dentro da estrutura acadêmica.
    **Tags associadas:**
    ["#ATIVIDADES-DE-DIRECAO-E-ADMINISTRACAO", "#DIRECAO-E-ADMINISTRACAO", "#ATIVIDADES-DE-ENSINO", "#ENSINO","#DISCIPLINA", "#ATIVIDADES-DE-ESTAGIO", "#ESTAGIO", "#ATIVIDADES-DE-EXTENSAO-UNIVERSITARIA", "#EXTENSAO-UNIVERSITARIA", "#ATIVIDADES-DE-TREINAMENTO-MINISTRADO", "#TREINAMENTO-MINISTRADO", "#OUTRAS-ATIVIDADES-TECNICO-CIENTIFICA", "#OUTRA-ATIVIDADE-TECNICO-CIENTIFICA", "#ORGANIZACAO-DE-EVENTO", "#DADOS-COMPLEMENTARES", "#INFORMACOES-ADICIONAIS","#INFORMACOES-ADICIONAIS-INSTITUICOES", "#INFORMACAO-ADICIONAL-INSTITUICAO", "#INFORMACOES-ADICIONAIS-CURSOS", "#INFORMACAO-ADICIONAL-CURSO"]
    
8. **Produção Bibliográfica**  
    **Significado:**  
    Abrange publicações acadêmicas como artigos científicos, livros, capítulos de livros, resumos em anais, trabalhos completos, entre outros materiais bibliográficos.  
    **Tags associadas:**
    ["#PRODUCAO-BIBLIOGRAFICA", "#TRABALHOS-EM-EVENTOS", "#TRABALHO-EM-EVENTOS", "#ARTIGOS-PUBLICADOS", "#ARTIGO-PUBLICADO", "#ARTIGOS-ACEITOS-PARA-PUBLICACAO", "#ARTIGO-ACEITO-PARA-PUBLICACAO", "#LIVROS-E-CAPITULOS", "#LIVROS-PUBLICADOS-OU-ORGANIZADOS", "#CAPITULOS-DE-LIVROS-PUBLICADOS", "#TEXTOS-EM-JORNAIS-OU-REVISTAS", "#DEMAIS-TIPOS-DE-PRODUCAO-BIBLIOGRAFICA", "#PARTITURA-MUSICAL", "#PREFACIO-POSFACIO", "#TRADUCAO"]
    
9. **Produção Técnica e Tecnológica**  
    **Significado:**  
    Diz respeito à produção aplicada, como desenvolvimento de softwares, patentes, protótipos, relatórios técnicos, pareceres e produtos tecnológicos.  
    **Tags associadas:
    ["#PRODUCAO-TECNICA", "#REGISTRO-OU-PATENTE", "#SOFTWARE", "#PRODUTO-TECNOLOGICO", "#PATENTE", "#CULTIVAR-PROTEGIDA", "#CULTIVAR-REGISTRADA", "#DESENHO-INDUSTRIAL", "#MARCA", "#TOPOGRAFIA-DE-CIRCUITO-INTEGRADO", "#PROCESSOS-OU-TECNICAS", "#TRABALHO-TECNICO", "#DEMAIS-TIPOS-DE-PRODUCAO-TECNICA", "#CARTA-MAPA-OU-SIMILAR", "#DESENVOLVIMENTO-DE-MATERIAL-DIDATICO-OU-INSTRUCIONAL", "#EDITORACAO", "#MANUTENCAO-DE-OBRA-ARTISTICA", "#MAQUETE", "#PROGRAMA-DE-RADIO-OU-TV", "#MIDIA-SOCIAL-WEBSITE-BLOG"]
    
10. **Produção Artística e Cultural**  
    **Significado:**  
    Inclui obras artísticas, exposições, performances, composições, curadorias e demais produções voltadas à expressão cultural e artística.  
    **Tags associadas:**
    ["#PRODUCAO-ARTISTICA-CULTURAL", "#APRESENTACAO-DE-OBRA-ARTISTICA", "#APRESENTACAO-EM-RADIO-OU-TV", "#ARRANJO-MUSICAL", "#COMPOSICAO-MUSICAL", "#OBRA-DE-ARTES-VISUAIS", "#OUTRA-PRODUCAO-ARTISTICA-CULTURAL", "#SONOPLASTIA", "#ARTES-CENICAS", "#ARTES-VISUAIS", "#MUSICA"]
    

### Fim da Lista de categorias ###

## Instruções: ##

- Escolha apenas uma das Categorias.
- Responda a categoria com todas as informações relacionadas a categoria provenientes da lista de categorias.
- Caso a entrada seja ambígua ou genérica, escolha a categoria mais provável com base no conteúdo principal.
- 
## Fim das Instruções ##

## Exemplo de uso ##

Entrada: Qual a experiência do pesquisador na produção de artigos na área de Inteligência Artificial?

Saída: 
8. **Produção Bibliográfica**  
    **Significado:**  
    Abrange publicações acadêmicas como artigos científicos, livros, capítulos de livros, resumos em anais, trabalhos completos, entre outros materiais bibliográficos.  
    **Tags associadas:**
    ["#PRODUCAO-BIBLIOGRAFICA", "#TRABALHOS-EM-EVENTOS", "#TRABALHO-EM-EVENTOS", "#ARTIGOS-PUBLICADOS", "#ARTIGO-PUBLICADO", "#ARTIGOS-ACEITOS-PARA-PUBLICACAO", "#ARTIGO-ACEITO-PARA-PUBLICACAO", "#LIVROS-E-CAPITULOS", "#LIVROS-PUBLICADOS-OU-ORGANIZADOS", "#CAPITULOS-DE-LIVROS-PUBLICADOS", "#TEXTOS-EM-JORNAIS-OU-REVISTAS", "#DEMAIS-TIPOS-DE-PRODUCAO-BIBLIOGRAFICA", "#PARTITURA-MUSICAL", "#PREFACIO-POSFACIO", "#TRADUCAO"]

## Fim dos Exemplos de Uso ##
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "developer", "content": system},
            {"role": "user", "content": f"Prompt a ser analisado: {user_input}"}
        ]
    )
    
    return completion.choices[0].message.content
