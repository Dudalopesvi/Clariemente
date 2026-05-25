import re
import hashlib

from ui.utils import exibir_cabecalho
from data.data_manager import carregar_dados, salvar_dados
import core.tarefas as core_tarefas
import core.ia_service as ia_service

# Perfis válidos de TDAH (RF01 – RN03)
PERFIS_TDAH = {
    "1": "desatento",
    "2": "hiperativo",
    "3": "combinado",
}

ROTULOS_PERFIL = {
    "desatento": "Desatento",
    "hiperativo": "Hiperativo/Impulsivo",
    "combinado": "Combinado",
}


# ---------------------------------------------------------------------------
# Helpers de validação (RF01)
# ---------------------------------------------------------------------------
def _validar_email(email: str) -> bool:
    """RN01 – Formato básico de e-mail."""
    return bool(re.match(r"^[\w\.\+\-]+@[\w\-]+\.[a-z]{2,}$", email, re.IGNORECASE))


def _validar_senha(senha: str) -> bool:
    """RN02 – Mínimo 8 caracteres, letras e números."""
    return (
        len(senha) >= 8
        and any(c.isalpha() for c in senha)
        and any(c.isdigit() for c in senha)
    )


def _hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


# ---------------------------------------------------------------------------
# RF01 – Cadastro de Perfil de Usuário
# ---------------------------------------------------------------------------
def criar_usuario_menu(dados: dict):
    exibir_cabecalho("CRIAR NOVO PERFIL – CLARIMENTE")

    # Nome
    nome = input("Nome de usuário: ").strip()
    if not nome:
        input("\n⚠ Nome não pode ser vazio. (Enter para continuar)")
        return
    if nome in dados:
        input("\n⚠ Nome já cadastrado. Escolha outro. (Enter para continuar)")
        return

    # E-mail (RN01)
    email = input("E-mail: ").strip()
    if not _validar_email(email):
        input("\n⚠ E-mail inválido (ex.: usuario@dominio.com). (Enter)")
        return
    emails_existentes = [u.get("email", "") for u in dados.values()]
    if email in emails_existentes:
        input("\n⚠ E-mail já cadastrado. (Enter)")
        return

    # Senha (RN02)
    senha = input("Senha (mín. 8 caracteres, letras e números): ").strip()
    if not _validar_senha(senha):
        input("\n⚠ Senha fraca. Use ao menos 8 caracteres com letras e números. (Enter)")
        return

    # Tipo TDAH (RN03)
    print("\nSelecione seu perfil de TDAH:")
    print("  1. Desatento")
    print("  2. Hiperativo/Impulsivo")
    print("  3. Combinado")
    perfil_opcao = input("\nOpção (1/2/3): ").strip()
    if perfil_opcao not in PERFIS_TDAH:
        input("\n⚠ Seleção de perfil obrigatória. (Enter)")
        return
    perfil_tdah = PERFIS_TDAH[perfil_opcao]

    # Preferência de comunicação
    print("\nEstilo de instrução:")
    print("  1. Direto e curto (recomendado)")
    print("  2. Detalhado e explicativo")
    pref = input("Opção: ").strip()
    estilo = "direto" if pref == "1" else "detalhado"

    dados[nome] = {
        "email": email,
        "senha": _hash_senha(senha),
        "perfil_tdah": perfil_tdah,
        "preferencias": {"estilo_instrucao": estilo},
        "tarefas_diarias": [],
        "tarefas_educacionais": [],
    }
    salvar_dados(dados)
    input(f"\n✅ Perfil [{nome}] criado com sucesso! (Enter)")


# ---------------------------------------------------------------------------
# RF02 – Gerenciamento de Tarefas
# ---------------------------------------------------------------------------
def _exibir_tarefas(tarefas: list, limite_ativas: bool = True):
    """Exibe tarefas com prioridade e prazo; respeita RN03 (máx. 5 ativas)."""
    ativas = core_tarefas.tarefas_ativas(tarefas) if limite_ativas else tarefas
    concluidas = [t for t in tarefas if t["concluida"]]

    if not ativas and not concluidas:
        print("  [Nenhuma tarefa ainda.]")
        return

    if ativas:
        print("── ATIVAS (ordenadas por prioridade) ──")
        for idx, t in enumerate(ativas, 1):
            prio = t.get("prioridade", "média").upper()
            prazo = f"  📅 {t['prazo']}" if t.get("prazo") else ""
            print(f"  {idx}. [ ] [{prio}] {t['titulo']}{prazo}")
            for p in t.get("passos", []):
                marca = "✓" if p.get("concluido") else "○"
                print(f"       {marca} {p['texto']}")

    total_pendentes = len([t for t in tarefas if not t["concluida"]])
    if total_pendentes > 5:
        print(f"\n  ℹ {total_pendentes - 5} tarefa(s) em fila de espera.")

    if concluidas:
        print(f"\n── CONCLUÍDAS ({len(concluidas)}) ──")
        for t in concluidas:
            print(f"  ✅ {t['titulo']}")


def gerenciar_tarefas_menu(dados: dict, usuario: str, chave: str, titulo: str):
    perfil_tdah = dados[usuario].get("perfil_tdah", "combinado")

    while True:
        exibir_cabecalho(titulo)
        tarefas = dados[usuario][chave]
        _exibir_tarefas(tarefas)

        print("\n" + "─" * 40)
        print("1. Criar Tarefa")
        print("2. Alternar Status (concluir/reabrir)")
        print("3. Excluir Tarefa")
        print("4. 🤖 Quebrar Tarefa com IA (Micro-Etapas)")
        print("5. 🆘 SOS – Tô Travado")
        print("6. Voltar")
        opcao = input("\nEscolha: ").strip()

        # --- Criar Tarefa ---
        if opcao == "1":
            nome = input("Nome da tarefa: ").strip()
            print("Prioridade: 1. Alta  2. Média  3. Baixa")
            prio_map = {"1": "alta", "2": "média", "3": "baixa"}
            prio = prio_map.get(input("Opção (Enter = Média): ").strip(), "média")
            prazo = input("Prazo (opcional, ex: 28/05): ").strip()
            ok, msg = core_tarefas.adicionar_tarefa(dados, usuario, chave, nome, prio, prazo)
            input(f"\n{'✅' if ok else '⚠'} {msg} (Enter)")

        # --- Alternar Status ---
        elif opcao == "2":
            ativas = core_tarefas.tarefas_ativas(tarefas)
            if not ativas:
                input("\nNenhuma tarefa ativa. (Enter)")
                continue
            try:
                idx_ativa = int(input("Número da tarefa: ")) - 1
                tarefa_alvo = ativas[idx_ativa]
                idx_real = tarefas.index(tarefa_alvo)
                core_tarefas.alternar_status_tarefa(dados, usuario, chave, idx_real)
            except (ValueError, IndexError):
                input("\n⚠ Número inválido. (Enter)")

        # --- Excluir Tarefa (RN04 – confirmação) ---
        elif opcao == "3":
            ativas = core_tarefas.tarefas_ativas(tarefas)
            if not ativas:
                input("\nNenhuma tarefa ativa para excluir. (Enter)")
                continue
            try:
                idx_ativa = int(input("Número da tarefa a excluir: ")) - 1
                tarefa_alvo = ativas[idx_ativa]
                confirma = input(
                    f"\n⚠ Confirma exclusão de '{tarefa_alvo['titulo']}'? (s/n): "
                ).strip().lower()
                if confirma == "s":
                    idx_real = tarefas.index(tarefa_alvo)
                    core_tarefas.excluir_tarefa(dados, usuario, chave, idx_real)
                    input("✅ Tarefa excluída. (Enter)")
                else:
                    input("Exclusão cancelada. (Enter)")
            except (ValueError, IndexError):
                input("\n⚠ Número inválido. (Enter)")

        # --- Quebrar com IA (RF03) ---
        elif opcao == "4":
            ativas = core_tarefas.tarefas_ativas(tarefas)
            if not ativas:
                input("\nNenhuma tarefa ativa. (Enter)")
                continue
            try:
                idx_ativa = int(input("Número da tarefa para a IA quebrar: ")) - 1
                tarefa_alvo = ativas[idx_ativa]
                idx_real = tarefas.index(tarefa_alvo)
                print("\n🤖 Gerando micro-etapas adaptadas ao seu perfil...")
                passos = ia_service.gerar_passos_tarefa(tarefa_alvo["titulo"], perfil_tdah)
                print(f"\n📋 Micro-etapas para '{tarefa_alvo['titulo']}':")
                for i, p in enumerate(passos, 1):
                    print(f"  {i}. {p}")
                if input("\nAceitar e salvar? (s/n): ").lower() == "s":
                    core_tarefas.injetar_passos_ia(dados, usuario, chave, idx_real, passos)
                    input("✅ Micro-etapas salvas! (Enter)")
                else:
                    input("Cancelado. (Enter)")
            except (ValueError, IndexError):
                input("\n⚠ Número inválido. (Enter)")

        # --- SOS Tô Travado (RF04 – RN01) ---
        elif opcao == "5":
            ativas = core_tarefas.tarefas_ativas(tarefas)
            if not ativas:
                input("\nNenhuma tarefa ativa. (Enter)")
                continue
            try:
                idx_ativa = int(input("Em qual tarefa você está travado? (número): ")) - 1
                tarefa_alvo = ativas[idx_ativa]
                print()
                for linha in ia_service.sos_travado(tarefa_alvo["titulo"], perfil_tdah):
                    print(f"  {linha}")
                input("\n(Enter para continuar)")
            except (ValueError, IndexError):
                input("\n⚠ Número inválido. (Enter)")

        elif opcao == "6":
            break


# ---------------------------------------------------------------------------
# RF04 – Chatbot Adaptável
# ---------------------------------------------------------------------------
def painel_ia_menu(dados: dict, usuario: str):
    exibir_cabecalho("ASSISTENTE CLARIMENTE")
    perfil_tdah = dados[usuario].get("perfil_tdah", "combinado")
    rotulo = ROTULOS_PERFIL.get(perfil_tdah, perfil_tdah.title())

    print(f"Perfil ativo: {rotulo}")
    print("Peça ajuda, faça perguntas ou diga o que está sentindo.")
    print("Comandos especiais: 'sos' → SOS Tô Travado  |  'sair' → voltar\n")

    _historico_respostas = []  # RN04 – evitar repetição

    while True:
        pergunta = input("Você: ").strip()
        if not pergunta:
            continue
        if pergunta.lower() == "sair":
            break
        if pergunta.lower() == "sos":
            tarefa = input("Nome da tarefa em que está travado: ").strip()
            for linha in ia_service.sos_travado(tarefa or "tarefa atual", perfil_tdah):
                print(f"  {linha}")
            print()
            continue

        print("\n🤖 Processando...")
        respostas = ia_service.obter_resposta_ia(pergunta, perfil_tdah)

        # RN04 – verifica repetição consecutiva
        if respostas == _historico_respostas:
            respostas = ["Tente reformular a pergunta para eu ajudar melhor!",
                         "Você consegue. Estou aqui com você. 💙"]
        _historico_respostas = respostas

        print(f"\n[ClariMente – {rotulo}]:")
        for linha in respostas:
            print(f"  {linha}")
        print()


# ---------------------------------------------------------------------------
# Painel principal do usuário
# ---------------------------------------------------------------------------
def painel_principal_menu(dados: dict, usuario: str):
    perfil = dados[usuario].get("perfil_tdah", "combinado")
    rotulo = ROTULOS_PERFIL.get(perfil, perfil.title())

    while True:
        exibir_cabecalho(f"OLÁ, {usuario.upper()} | Perfil: {rotulo}")
        print("1. Tarefas Diárias")
        print("2. Tarefas Educacionais")
        print("3. 🤖 Assistente ClariMente (Chat)")
        print("4. Logout")
        opcao = input("\nEscolha: ").strip()

        if opcao == "1":
            gerenciar_tarefas_menu(dados, usuario, "tarefas_diarias", "ROTINA DIÁRIA")
        elif opcao == "2":
            gerenciar_tarefas_menu(dados, usuario, "tarefas_educacionais", "ESTUDOS E EDUCAÇÃO")
        elif opcao == "3":
            painel_ia_menu(dados, usuario)
        elif opcao == "4":
            break
