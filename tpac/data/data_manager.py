
import json
import os

ARQUIVO_USUARIOS = "tpac_users.json"

def carregar_dados() -> dict:
    if os.path.exists(ARQUIVO_USUARIOS):
        with open(ARQUIVO_USUARIOS, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def salvar_dados(dados: dict):
    with open(ARQUIVO_USUARIOS, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

