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
    
    system = """
Você é um assistente que atua como um classificador inteligente. Sua tarefa é ler um prompt fornecido por um usuário e determinar, com base em uma lista de tags disponíveis, quais delas melhor se alinham com o conteúdo e intenção do prompt.

Para isso, siga as seguintes instruções:
- Analise cuidadosamente o conteúdo do prompt.
- Selecione apenas as tags mais relevantes.
- As tags devem estar exatamente como na lista abaixo.
- Retorne apenas a lista de tags mais adequadas, sem explicações adicionais.
- Responda no seguinte formato: ["#TAG1", "#TAG2", "#TAG3"]

### LISTA DE TAGS DISPONÍVEIS ###

1. Identificação Pessoal e Profissional
#CURRICULO-VITAE: Documento que reúne todas as informações sobre a trajetória acadêmica e profissional.
#DADOS-GERAIS: Informações básicas sobre o indivíduo, como nome completo, nacionalidade e afiliações.
#RESUMO-CV: Síntese da trajetória profissional e acadêmica, destacando principais áreas de atuação.
#OUTRAS-INFORMACOES-RELEVANTES: Detalhes adicionais que não se encaixam nas categorias padrão, mas são importantes.

2. Informações de Contato
#ENDERECO: Informações gerais de localização do indivíduo.
#ENDERECO-PROFISSIONAL: Endereço da instituição ou empresa onde o profissional trabalha.
#ENDERECO-RESIDENCIAL: Endereço pessoal do profissional.

3. Áreas de Atuação e Conhecimento
#PALAVRAS-CHAVE: Termos que descrevem as especialidades e competências do profissional.
#AREAS-DO-CONHECIMENTO: Campos do saber em que o profissional possui conhecimento e experiência.
#AREA-DO-CONHECIMENTO-1: Classificação detalhada das áreas específicas em que o profissional atua.
#AREA-DO-CONHECIMENTO-2: Classificação detalhada das áreas específicas em que o profissional atua.
#AREA-DO-CONHECIMENTO-3: Classificação detalhada das áreas específicas em que o profissional atua.
#SETORES-DE-ATIVIDADE: Indústrias ou segmentos onde o profissional desenvolve suas atividades.

4. Formação Acadêmica e Qualificações
#FORMACAO-ACADEMICA-TITULACAO: Histórico dos títulos acadêmicos obtidos.
#CURSO-TECNICO-PROFISSIONALIZANTE: Formação técnica voltada para o mercado de trabalho.
#ENSINO-FUNDAMENTAL-PRIMEIRO-GRAU: Escolaridade básica inicial.
#ENSINO-MEDIO-SEGUNDO-GRAU: Formação intermediária antes do ensino superior.
#GRADUACAO: Curso superior concluído pelo profissional.
#APERFEICOAMENTO: Cursos de aprimoramento técnico ou acadêmico.
#ESPECIALIZACAO: Formação adicional focada em determinada área profissional.
#MESTRADO: Pós-graduação voltada à pesquisa ou aplicação profissional.
#MESTRADO-PROFISSIONALIZANTE: Pós-graduação voltada à aplicação profissional.
#DOUTORADO: Formação avançada baseada em pesquisa acadêmica.
#RESIDENCIA-MEDICA: Programa de especialização para médicos em determinada área.
#LIVRE-DOCENCIA: Título concedido em algumas instituições como avanço acadêmico.
#POS-DOUTORADO: Pesquisa avançada após o doutorado.

5. Pesquisa e Projetos Acadêmicos
#DISCIPLINA: Matérias ministradas ou estudadas pelo profissional.
#LINHA-DE-PESQUISA: Áreas temáticas de investigação acadêmica.
#PROJETO-DE-PESQUISA: Estudos e investigações desenvolvidos.
#EQUIPE-DO-PROJETO: Profissionais e acadêmicos envolvidos nas pesquisas.
#INTEGRANTES-DO-PROJETO: Profissionais e acadêmicos envolvidos nas pesquisas.
#FINANCIADORES-DO-PROJETO: Entidades que fornecem apoio financeiro para a pesquisa.
#PRODUCOES-CT-DO-PROJETO: Resultados acadêmicos e técnicos oriundos do projeto.

6. Orientações e Treinamentos
#ORIENTACOES: Supervisão de estudantes em trabalhos acadêmicos.
#ORIENTACAO: Supervisão de estudantes em trabalhos acadêmicos.
#TREINAMENTO: Programas de capacitação ministrados ou realizados.

7. Experiência Profissional
#ATUACOES-PROFISSIONAIS: Experiência adquirida no mercado de trabalho.
#ATUACAO-PROFISSIONAL: Experiência adquirida no mercado de trabalho.
#VINCULOS: Relação formal entre o profissional e as instituições onde trabalhou.

8. Atividades Acadêmicas e Administrativas
#ATIVIDADES-DE-DIRECAO-E-ADMINISTRACAO: Funções de liderança e gestão acadêmica.
#ATIVIDADES-DE-PESQUISA-E-DESENVOLVIMENTO: Trabalhos científicos e tecnológicos.
#ATIVIDADES-DE-ENSINO: Docência e instrução em cursos acadêmicos.
#ATIVIDADES-DE-ESTAGIO: Experiência prática adquirida por meio de estágios.
#ATIVIDADES-DE-SERVICO-TECNICO-ESPECIALIZADO: Prestação de serviços especializados.
#ATIVIDADES-DE-EXTENSAO-UNIVERSITARIA: Projetos de interação entre a universidade e a sociedade.
#ATIVIDADES-DE-TREINAMENTO-MINISTRADO: Cursos e capacitações conduzidos pelo profissional.
#ATIVIDADES-DE-CONSELHO-COMISSAO-E-CONSULTORIA: Participação em comitês e grupos consultivos.

9. Habilidades e Reconhecimentos
#IDIOMAS: Línguas faladas e nível de proficiência.
#PREMIOS-TITULOS: Prêmios e reconhecimentos obtidos ao longo da carreira.
#LICENCAS: Certificações e permissões profissionais.

10. Produção Bibliográfica
#PRODUCAO-BIBLIOGRAFICA: Conjunto das publicações acadêmicas do profissional.
#ARTIGOS-PUBLICADOS: Trabalhos científicos revisados e publicados.
#ARTIGOS-ACEITOS-PARA-PUBLICACAO: Trabalhos científicos aceitos para publicação.
#LIVROS-E-CAPITULOS: Obras escritas ou capítulos contribuídos.
#TEXTOS-EM-JORNAIS-OU-REVISTAS: Publicações voltadas para o público geral.
#OUTRA-PRODUCAO-BIBLIOGRAFICA: Trabalhos acadêmicos que não se enquadram nas categorias anteriores.
#TRADUCAO: Trabalhos de tradução acadêmica ou literária.

11. Produção Técnica e Tecnológica
#PRODUCAO-TECNICA: Trabalhos técnicos desenvolvidos pelo profissional.
#REGISTRO-OU-PATENTE: Propriedade intelectual protegida.
#PATENTE: Propriedade intelectual protegida.
#SOFTWARE: Programas e sistemas desenvolvidos.
#PRODUTO-TECNOLOGICO: Inovações tecnológicas criadas.
#CULTIVAR-PROTEGIDA: Desenvolvimento de novas variedades agrícolas registradas.
#DESENHO-INDUSTRIAL: Criações visuais registradas.
#MARCA: Marcas registradas.
#PROCESSOS-OU-TECNICAS: Novos métodos e técnicas desenvolvidos.
#TRABALHO-TECNICO: Estudos e relatórios técnicos aplicados.

12. Produção Artística e Cultural
#PRODUCAO-ARTISTICA-CULTURAL: Trabalhos desenvolvidos na área cultural e artística.
#APRESENTACAO-DE-OBRA-ARTISTICA: Exibições públicas de produções artísticas.
#OBRA-DE-ARTES-VISUAIS: Pinturas, esculturas e outras formas visuais de arte.
#COMPOSICAO-MUSICAL: Criação de músicas e trilhas sonoras.
#PROGRAMA-DE-RADIO-OU-TV: Produção de conteúdos para mídia tradicional.
#MIDIA-SOCIAL-WEBSITE-BLOG: Desenvolvimento de conteúdo digital e online.

### FIM DA LISTA DE TAGS ###
"""
    
    completion = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18", 
        messages= [
            {"role": "developer", "content": system},
            {"role": "user", "content": f"Prompt a ser analisado: {user_input}"}
        ]
    )
    
    return completion.choices[0].message.content
