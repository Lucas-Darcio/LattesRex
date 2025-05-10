import os
import sys
import streamlit as st
import json
import tiktoken

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.business_logic.resume_processor import process_resume
from app.business_logic.query_handler import  extract_attributes_chatbot, handle_query_chat

from app.data_access.file_manager import list_curriculos, load_curriculo
#from app.services.email_service import send_email

from app.business_logic.compression_utils import extract_prompt_tags

from app.api.openai_api import extract_related_tags

# Diretório onde os currículos armazenados ficam
CURRICULO_DIR = "curriculos/"

# Caminho para o arquivo JSON
CONSULTAS_DIR = "consultas/"

