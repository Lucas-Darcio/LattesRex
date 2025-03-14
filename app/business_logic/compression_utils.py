import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
import xmltodict
import os
import json
import re

def read_json(json_file_path):
    with open(json_file_path, "r") as f:
        file = json.load(f)
    return file

def read_file(xml_file_path):
    """
    Returns the read file as a string.
    """
    file = open(xml_file_path,'r',encoding='latin-1')
    return file.read()

# Converte um arquivo XML para Dictionary
def xml_to_dict(xml_file_path):
    """
    Returns the given file as a JSON-like dictionary.
    """
    contents = read_file(xml_file_path)
    extracted_data = xmltodict.parse(contents)
    return extracted_data


def compact_name(name, existing_names, is_tag=True):
    """
    Given a tag or attribute name and a dictionary of the names that 
    already exist, adds an abbreviated version of the name to the 
    dictionary and returns the abbreviation.
    """
    # Generate a compacted version of the name
    compacted = ''.join(word[0] for word in name.split('-'))
    
    # Ensure the compacted name is unique by adding numbers if necessary
    candidates = {k: v for k, v in existing_names.items() if k.split("_")[0] == compacted and v == name}

    if (compacted in existing_names.keys()) and (candidates == {}):
        # if not is_tag: 
        #     print(candidates, name, compacted, existing_names[compacted])
        #     print()
        i = 1
        new_compacted = compacted + "_" + str(i)
        while new_compacted in existing_names:
            i += 1
            new_compacted = compacted + "_" + str(i)
        compacted = new_compacted
    

    # Add the compacted name to the set of existing names
    existing_names[compacted] = name
    
    return compacted

def parse_and_compact_xml_full(file_path):
    """
    Creates a new XML file with the tags and attributes compressed into 
    abbreviated versions.
    """
    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Dictionaries to store original and compacted names
    tag_dict = {}
    attribute_dict = {}
    
    # Sets to keep track of existing compacted names to avoid collisions
    #existing_tag_names = {} #set()
    #existing_attribute_names = {} #set()
    
    # Function to recursively process each element
    def process_element(element):
        # Compact the tag name
        original_tag = element.tag
        compacted_tag = compact_name(original_tag, tag_dict)
        #tag_dict[compacted_tag] = original_tag
        element.tag = compacted_tag
        
        # Compact attribute names
        new_attributes = {}
        for original_attr, value in element.attrib.items():
            compacted_attr = compact_name(original_attr, attribute_dict, False)
            #attribute_dict[compacted_attr] = original_attr
            new_attributes[compacted_attr] = value
        element.attrib = new_attributes
        
        # Recursively process child elements
        for child in element:
            process_element(child)
    
    # Start processing from the root element
    process_element(root)
    
    # Save the modified XML to a new file
    #print(type(file_path), file_path)
    compacted_file_path = str(file_path).replace('.xml', '_full_compacted.xml')
    tree.write(compacted_file_path, encoding='utf-8', xml_declaration=True)
    
    return compacted_file_path, tag_dict, attribute_dict


def generate_compressed_dict(xml_file_path):
    """
    Given a XML file path, parses and compresses its tags and attributes. 
    Returns a dictionary containing the file converted to a JSON-like dict, 
    the tag and attribute dicts, and the file name.

    ##### Dictionary keys:
    - converted file: `"RESUME"`
    - tag dict: `"TAG DICTIONARY"`
    - attribute dict: `"ATTRIBUTE DICTIONARY"`
    - file name: `"FILENAME"`
    """
    xml_file_path = str(xml_file_path)
    compacted_file_path, tag_dict, attribute_dict = parse_and_compact_xml_full(xml_file_path)
    compressed_dict = xml_to_dict(compacted_file_path)
    os.remove(compacted_file_path)
    return {'RESUME': compressed_dict, 'TAG DICTIONARY': tag_dict, 'ATTRIBUTE DICTIONARY': attribute_dict, 'FILENAME': xml_file_path.split("/")[-1]}


def get_char_len(obj):
    return len(obj.__str__())

def calculate_gain(og, new):
    return 100 * (og-new)/og

def summarize_gains(original_dict, compressed_data):
    """
    Given a JSON-like dict of the XML file, and the compressed data generated from the 
    same XML, calculate gains of size for the compressed version.
    """
    original_num_char = get_char_len(original_dict)
    compressed_num_char = get_char_len(compressed_data['RESUME'])
    full_compr_num_char = get_char_len(compressed_data)

    print(f"(Filename: {compressed_data['FILENAME']})")
    print(f"Original: {original_num_char}")
    print(f"Compressed: {compressed_num_char}")
    print(f"Compressed + schema: {full_compr_num_char}")
    print(f"\tTag dictionary: {get_char_len(compressed_data['TAG DICTIONARY'])}")
    print(f"\tAttribute dictionary: {get_char_len(compressed_data['ATTRIBUTE DICTIONARY'])}")
    print(f"Gain: {calculate_gain(original_num_char,compressed_num_char):.4f}%")
    print(f"With schema: {calculate_gain(original_num_char, full_compr_num_char):.4f}%")

def write_compressed_data_to_file(compressed_data, output_dir):
    filename = compressed_data['FILENAME']
    with open(output_dir + "processed_" + filename.replace('.xml', '.txt'), "w") as f:
        for k, v in compressed_data.items():
            f.write(f"### START OF {k} ###\n")
            f.write(f"{v}\n".replace('{', '<').replace('}', '>'))
            f.write(f"'### END OF {k} ###\n\n")
            

"""
Extrai as tags de um prompt e retorna o texto sem as tags e a lista de tags encontradas.

:param prompt: O texto do prompt contendo tags no formato "#tag"
:return: Uma tupla onde o primeiro item é o prompt sem as tags e o segundo item 
é a lista de tags extraídas.
"""         
def extract_prompt_tags(prompt: str) -> tuple[str, list[str]]:
    """
    Extrai as tags de um prompt e retorna o texto sem as tags e a lista de tags encontradas.
    
    :param prompt: O texto do prompt contendo tags no formato "#tag"
    :return: Uma tupla onde o primeiro item é o prompt sem as tags e o segundo item é a lista de tags extraídas.
    """
    words = prompt.split()
    tags = []
    cleaned_words = []
    
    collecting_tag = False
    current_tag = ""
    
    for word in words:
        if word.startswith("#"):
            if collecting_tag:
                tags.append(current_tag)
            current_tag = word
            collecting_tag = True
        elif collecting_tag and ("-" in word or word.isalnum()):
            current_tag += " " + word
        else:
            if collecting_tag:
                tags.append(current_tag)
                collecting_tag = False
            cleaned_words.append(word)
    
    if collecting_tag:
        tags.append(current_tag)
    
    cleaned_prompt = " ".join(cleaned_words)
    return cleaned_prompt, tags

# with open("altigran.json", "w") as f:
#     json.dump(xml_to_dict("/home/amanda_spellen/code/pibic/feedback_app/lattes_llm_v3/app/business_logic/Altigran Soares da Silva.xml"), f)