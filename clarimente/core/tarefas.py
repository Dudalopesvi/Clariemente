from data.data_manager import salvar_dados

PRIORIDADES_VALIDAS = {"alta", "média", "baixa"}
LIMITE_TAREFAS_ATIVAS = 5  # RN03 – máximo de tarefas exibidas


def adicionar_tarefa(dados: dict, usuario: str, chave: str, titulo: str,
                     prioridade: str = "média", prazo: str = ""):
    """
    RF02 – Cria tarefa com nome, prioridade e prazo opcional.
    RN01 – Nome obrigatório.
    RN02 – Prioridade padrão Média se não informada.
    """
    titulo = titulo.strip()
    if not titulo:
        return False, "O nome da tarefa é obrigatório."  # RN01

    prioridade = prioridade.strip().lower()
    if prioridade not in PRIORIDADES_VALIDAS:
        prioridade = "média"  # RN02

    dados[usuario][chave].append({
        "titulo": titulo,
        "prioridade": prioridade,
        "prazo": prazo.strip(),
        "concluida": False,
        "passos": []
    })
    salvar_dados(dados)
    return True, "Tarefa criada com sucesso."


def alternar_status_tarefa(dados: dict, usuario: str, chave: str, idx: int):
    tarefas = dados[usuario][chave]
    if 0 <= idx < len(tarefas):
        tarefas[idx]["concluida"] = not tarefas[idx]["concluida"]
        salvar_dados(dados)
        return True
    return False


def excluir_tarefa(dados: dict, usuario: str, chave: str, idx: int) -> bool:
    """RF02 – RN04: confirmação feita na camada de menu antes de chamar esta função."""
    tarefas = dados[usuario][chave]
    if 0 <= idx < len(tarefas):
        tarefas.pop(idx)
        salvar_dados(dados)
        return True
    return False


def injetar_passos_ia(dados: dict, usuario: str, chave: str, idx: int, passos: list):
    """RF03 – Injeta micro-etapas geradas pela IA na tarefa selecionada."""
    tarefas = dados[usuario][chave]
    if 0 <= idx < len(tarefas):
        tarefas[idx]["passos"] = [{"texto": p, "concluido": False} for p in passos]
        salvar_dados(dados)


def tarefas_ativas(tarefas: list) -> list:
    """RF02 – RN03: retorna apenas as 5 tarefas não concluídas mais urgentes."""
    pendentes = [t for t in tarefas if not t["concluida"]]
    # Ordena por prioridade: alta > média > baixa
    ordem = {"alta": 0, "média": 1, "baixa": 2}
    pendentes.sort(key=lambda t: ordem.get(t.get("prioridade", "média"), 1))
    return pendentes[:LIMITE_TAREFAS_ATIVAS]
