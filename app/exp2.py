import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# Adiciona o diretório pai ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.data_access.file_manager import list_curriculos

# Caminho para os currículos
CURRICULO_DIR = "curriculos/"
stored_resumes = list_curriculos(CURRICULO_DIR)

# Carrega os dados
data_tokens = np.load("data_tokens.npy")  # Formato: (pessoas, tokens_por_pessoa)

num_pessoas = data_tokens.shape[0]
tokens_por_pessoa = data_tokens.shape[1]
valores = data_tokens.flatten()

# Cálculo da média geral
media = np.mean(valores)

# Inicializa o gráfico
plt.figure(figsize=(18, 7))

# Índice geral para barras
indice = 0
separadores = []

# Contadores para valores >1280000 e <=128000
maiores_128k = 0
menores_ou_iguais_128k = 0

for i in range(num_pessoas):
    pessoa_tokens = data_tokens[i]
    cor_pessoa = ['skyblue'] * len(pessoa_tokens)

    # Contagem dos valores maiores ou menores que 128.000
    maiores_128k += np.sum(pessoa_tokens > 128_000)
    menores_ou_iguais_128k += np.sum(pessoa_tokens <= 128_000)

    # Destaca o maior valor da pessoa
    max_idx_local = np.argmax(pessoa_tokens)
    cor_pessoa[max_idx_local] = 'orange'

    # Barras da pessoa
    plt.bar(range(indice, indice + len(pessoa_tokens)), pessoa_tokens, color=cor_pessoa)

    # Texto no maior valor
    max_valor = pessoa_tokens[max_idx_local]
    plt.text(indice + max_idx_local, max_valor + 2, f'{int(max_valor)}',
             ha='center', fontsize=8, fontweight='bold', color='darkorange')

    # Linha da média da pessoa
    media_pessoa = np.mean(pessoa_tokens)
    plt.hlines(media_pessoa, indice, indice + len(pessoa_tokens) - 1, colors='green', linestyles='dotted', linewidth=1.3)
    
    plt.text(indice + len(pessoa_tokens) - 1/2, media_pessoa + 10, f'{media_pessoa:.2f}', color='green', fontsize=10, ha='right')

    # Separação visual entre pessoas
    if i > 0:
        plt.axvline(indice - 0.5, color='gray', linestyle='--', linewidth=1)

    # Nome/ID da pessoa abaixo do eixo
    plt.text(indice + len(pessoa_tokens)/2, -5, stored_resumes[i].split()[0],
             ha='center', va='top', fontsize=8, rotation=0, color='gray')

    separadores.append(indice)
    indice += len(pessoa_tokens)

# Linha da média geral
plt.axhline(media, color='navy', linestyle='--', linewidth=0.8, label=f'Média Geral = {media:.2f}')
plt.text(indice - 1, media + 10, f'{media:.2f}', color='navy', fontsize=10, ha='right')

#limite da openai
plt.axhline(128000, color='red', linestyle='--', linewidth=0.8, label=f'Limite OpenAI = 128.000 tokens')
plt.text(indice - 1, 128000 + 10, f'128.000', color='red', fontsize=10, ha='right')

# Contador de valores >128k e <=128k como legenda
texto_contagem = f"> 128.000 tokens: {maiores_128k}  |  ≤ 128.000 tokens: {menores_ou_iguais_128k}"

# Linha invisível para representar as médias por pessoa
plt.plot([], [], color='green', linestyle='dotted', linewidth=1.3, label='Média por Pessoa')

# Cria uma linha invisível para usar na legenda
plt.plot([], [], ' ', label=texto_contagem)

# Legenda principal (inclui também a média geral, que já tem label)
plt.legend(loc='upper right')

plt.xlabel("Perguntas por currículo")
plt.ylabel("Tokens")
plt.title("Quantas perguntas passam do limite de tokens (128.000)")

plt.show()