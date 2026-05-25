import os

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def exibir_cabecalho(titulo: str):
    limpar_tela()
    print("=" * 60)
    print(f"{titulo.center(60)}")
    print("=" * 60 + "\n")