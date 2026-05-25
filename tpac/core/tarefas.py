from data.data_manager import salvar_dados

def adicionar_tarefa(dados: dict, usuario: str, chave: str, titulo: str):
    dados[usuario][chave].append({
        "titulo": titulo,
        "concluida": False,
        "passos": []
    })
    salvar_dados(dados)

def alternar_status_tarefa(dados: dict, usuario: str, chave: str, idx: int):
    tarefas = dados[usuario][chave]
    if 0 <= idx < len(tarefas):
        tarefas[idx]["concluida"] = not tarefas[idx]["concluida"]
        salvar_dados(dados)

def injetar_passos_ia(dados: dict, usuario: str, chave: str, idx: int, passos: list):
    tarefas = dados[usuario][chave]
    if 0 <= idx < len(tarefas):
        tarefas[idx]["passos"] = [{"texto": p, "concluido": False} for p in passos]
        salvar_dados(dados)