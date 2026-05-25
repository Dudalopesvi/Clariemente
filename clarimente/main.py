import sys
import os

# Garante que os imports relativos funcionem ao rodar como 'python main.py'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Carrega variáveis do .env (GEMINI_API_KEY) se python-dotenv estiver instalado
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass

from data.data_manager import carregar_dados
from ui.menus import criar_usuario_menu, painel_principal_menu, _hash_senha
from ui.utils import exibir_cabecalho


def executar_sistema():
    while True:
        dados = carregar_dados()
        exibir_cabecalho("CLARIMENTE – Assistente para TDAH")

        print("1. Entrar com perfil existente")
        print("2. Criar novo perfil")
        print("3. Encerrar")
        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            if not dados:
                input("\nNenhum perfil cadastrado. Crie um primeiro! (Enter)")
                continue

            nome = input("\nNome de usuário: ").strip()
            if nome not in dados:
                input("\n⚠ Perfil não encontrado. (Enter)")
                continue

            senha = input("Senha: ").strip()
            if dados[nome].get("senha") and dados[nome]["senha"] != _hash_senha(senha):
                input("\n⚠ Senha incorreta. (Enter)")
                continue

            painel_principal_menu(dados, nome)

        elif opcao == "2":
            criar_usuario_menu(dados)

        elif opcao == "3":
            print("\nAté logo! 💙")
            break


if __name__ == "__main__":
    executar_sistema()
