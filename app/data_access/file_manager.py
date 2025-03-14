import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path

def list_curriculos(directory):
    # Lista todos os currículos armazenados no diretório
    return [f for f in sorted(os.listdir(directory)) if f.endswith(".xml")]

def load_curriculo(choosen_file):
    # Carrega e processa um currículo armazenado no servidor
    choosen_file_name = choosen_file.name
    save_path = Path("curriculos", choosen_file_name)

    with open(save_path, mode='wb') as w:
        w.write(choosen_file.getvalue())

    return save_path
    # try:
    # except Exception as e:
    #     print(f"Error loading resume: {e}")
    #     return None

def carregar_consultas(filepath):
    # Função para carregar consultas de um arquivo JSON
    queries = {}
    for query_file in sorted(os.listdir(filepath)):
        with open(os.path.join(filepath, query_file), "r") as f:
            content = json.load(f)
            queries[content['titulo']] = content
            f.close()

    return queries