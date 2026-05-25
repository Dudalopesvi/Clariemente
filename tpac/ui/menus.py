from ui.utils import exibir_cabecalho
from data.data_manager import carregar_dados, salvar_dados
import core.tarefas as core_tarefas
import core.ia_service as ia_service

def criar_usuario_menu(dados: dict):
    exibir_cabecalho("CRIAR NOVO PERFIL")
    nome = input("Digite o nome do usuário: ").strip()
    if not nome or nome in dados:
        input("\nNome inválido ou já existente. Pressione Enter.")
        return

    print("\n--- Preferências de Comunicação ---")
    print("1. Passo a passo curto e direto (Recomendado para TPAC)")
    print("2. Detalhado e explicativo")
    pref = input("Opção: ").strip()
    estilo = "direto" if pref == "1" else "detalhado"

    dados[nome] = {
        "preferencias": {"estilo_instrucao": estilo},
        "tarefas_diarias": [],
        "tarefas_educacionais": []
    }
    salvar_dados(dados)
    input(f"\nPerfil [{nome}] criado! Pressione Enter.")

def gerenciar_tarefas_menu(dados: dict, usuario: str, chave: str, titulo: str):
    while True:
        exibir_cabecalho(titulo)
        tarefas = dados[usuario][chave]
        
        if not tarefas:
            print("[Nenhuma tarefa pendente.]")
        else:
            for idx, t in enumerate(tarefas, 1):
                status = "[X]" if t["concluida"] else "[ ]"
                print(f"{idx}. {status} {t['titulo']}")
                for p in t.get("passos", []):
                    print(f"   ○ {p['texto']}")

        print("\n" + "-"*30)
        print("1. Criar Tarefa | 2. Alternar Status | 3. 🤖 Desmembrar com IA | 4. Voltar")
        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            t_nome = input("Nome da tarefa: ").strip()
            if t_nome: core_ref = core_tarefas.adicionar_tarefa(dados, usuario, chave, t_nome)
        elif opcao == "2" and tarefas:
            try:
                idx = int(input("Número da tarefa: ")) - 1
                core_tarefas.alternar_status_tarefa(dados, usuario, chave, idx)
            except ValueError: pass
        elif opcao == "3" and tarefas:
            try:
                idx = int(input("Número da tarefa para IA tratar: ")) - 1
                if 0 <= idx < len(tarefas):
                    passos = ia_service.gerar_passos_tarefa(tarefas[idx]["titulo"])
                    print("\n🤖 Passos sugeridos pela IA:")
                    for i, p in enumerate(passos, 1): print(f"  {i}. {p}")
                    if input("\nAceitar sugestão? (s/n): ").lower() == 's':
                        core_tarefas.injetar_passos_ia(dados, usuario, chave, idx, passos)
            except ValueError: pass
        elif opcao == "4":
            break

def painel_ia_menu(dados: dict, usuario: str):
    exibir_cabecalho("ASSISTENTE DE IA PARA TPAC")
    print("Peça ajuda para simplificar enunciados, organizar rotinas ou tirar dúvidas.")
    print("Digite 'sair' para retornar.\n")
    estilo = dados[usuario]["preferencias"]["estilo_instrucao"]

    while True:
        pergunta = input("\nVocê: ").strip()
        if pergunta.lower() == 'sair': break
        if not pergunta: continue

        print("\n🤖 Processando sem ambiguidades...")
        respostas = ia_service.obter_resposta_ia(pergunta, estilo)
        print(f"\n[Assistente - Modo {estilo.upper()}]:")
        for linha in respostas:
            print(f"- {linha}")
        print("-" * 30)

def painel_principal_menu(dados: dict, usuario: str):
    while True:
        exibir_cabecalho(f"PAINEL DO USUÁRIO: {usuario}")
        print("1. Atividades Diárias\n2. Atividades Educacionais\n3. 🤖 Central de IA\n4. Logout")
        opcao = input("\nEscolha: ").strip()
        if opcao == "1":
            gerenciar_tarefas_menu(dados, usuario, "tarefas_diarias", "ROTINA DIÁRIA")
        elif opcao == "2":
            gerenciar_tarefas_menu(dados, usuario, "tarefas_educacionais", "ESTUDOS E EDUCAÇÃO")
        elif opcao == "3":
            painel_ia_menu(dados, usuario)
        elif opcao == "4":
            break