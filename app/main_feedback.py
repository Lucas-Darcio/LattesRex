import os
import sys
import streamlit as st

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.business_logic.resume_processor import process_resume
from app.business_logic.query_handler import handle_query, extract_attributes
from app.data_access.file_manager import list_curriculos, load_curriculo, carregar_consultas
from app.services.email_service import send_email
#from app.components.custom_css import inject_custom_css

# Diretório onde os currículos armazenados ficam
CURRICULO_DIR = "curriculos/"

# Caminho para o arquivo JSON
CONSULTAS_DIR = "consultas/"

