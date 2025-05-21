import xml.etree.ElementTree as ET
from business_logic.compression_utils import generate_compressed_dict, xml_to_dict

def process_resume(file):
    # Função para processar o arquivo XML em um dicionário
    try:
        resume_data = xml_to_dict(file)

        return resume_data
    except Exception as e:
        print(f"Error processing resume: {e}")
        return None
