def obter_resposta_ia(pergunta: str, estilo_usuario: str) -> list:
    """
    Simula ou conecta à API de IA. Retorna uma lista de strings 
    garantindo que o output seja focado, direto e sem ambiguidades.
    """
    # Se integrado à API real, o prompt exigiria respostas no formato abaixo
    if estilo_usuario == "direto":
        return [
            "Ação 1: Foque apenas no comando central.",
            "Ação 2: Reduza ruídos externos antes de iniciar.",
            "Ação 3: Faça uma pausa silenciosa de 5 minutos ao terminar."
        ]
    else:
        return [
            "Explicação: Para resolver esse problema, precisamos segmentar os estímulos.",
            "Passo Recomendado: Comece organizando visualmente seu caderno de estudos.",
            "Dica: O cansaço auditivo pode ser mitigado fragmentando o tempo de leitura."
        ]

def gerar_passos_tarefa(titulo_tarefa: str) -> list:
    """Quebra tarefas complexas em subtarefas visuais sequenciais."""
    return [
        "Organizar o espaço de trabalho retirando distrações visuais.",
        "Executar a primeira metade da atividade por 15 minutos.",
        "Fazer uma pausa de 5 minutos em silêncio absoluto."
    ]


# -------------------------------------------------------------------------------

# import os
# from google import genai
# from google.genai import types

# # Inicializa o cliente se a chave de API estiver presente
# API_KEY = os.environ.get("GEMINI_API_KEY")
# client = genai.Client() if API_KEY else None

# # Modelo ideal para tarefas rápidas de texto e resumos no terminal
# MODELO_GEMINI = "gemini-2.5-flash"


# def _obter_instrucao_tpac(estilo_usuario: str) -> str:
#     """Retorna a persona e as diretrizes de formatação da IA para o contexto de TPAC."""
#     base_prompt = (
#         "Você é um assistente especializado em acessibilidade para pessoas com TPAC "
#         "(Transtorno do Processamento Auditivo Central).\n"
#         "Seu papel é reduzir a carga cognitiva, cansaço mental e ambiguidade.\n"
#         "Diretrizes obrigatórias:\n"
#         "- Nunca use parágrafos longos, blocos densos de texto ou jargões complexos.\n"
#         "- Use frases curtas, ordem direta (Sujeito + Verbo + Objeto).\n"
#         "- Divida as respostas visualmente usando tópicos/bullets claros.\n"
#     )
    
#     if estilo_usuario == "direto":
#         base_prompt += "- Seja extremamente conciso. Vá direto ao ponto, use o mínimo de palavras possível."
#     else:
#         base_prompt += "- Se precisar explicar um conceito, faça-o em etapas lógicas e sequenciais simples."
        
#     return base_prompt


# def obter_resposta_ia(pergunta: str, estilo_usuario: str) -> list:
#     """Conecta ao Gemini para responder dúvidas gerais de estudos ou organização."""
#     if not client:
#         return ["Erro: Variável de ambiente GEMINI_API_KEY não configurada.", "Por favor, configure sua chave de API."]

#     system_instruction = _obter_instrucao_tpac(estilo_usuario)

#     try:
#         response = client.models.generate_content(
#             model=MODELO_GEMINI,
#             contents=pergunta,
#             config=types.GenerateContentConfig(
#                 system_instruction=system_instruction,
#                 temperature=0.3, # Baixa temperatura para manter a resposta factual e focada
#             ),
#         )
        
#         # Divide a resposta por linhas para bater com a estrutura de exibição da UI do terminal
#         return [linha.strip() for linha in response.text.split("\n") if linha.strip()]

#     except Exception as e:
#         return [f"Erro ao nos comunicarmos com a IA: {str(e)}"]


# def gerar_passos_tarefa(titulo_tarefa: str) -> list:
#     """Usa o Gemini para quebrar uma tarefa macro em micro-ações sequenciais."""
#     if not client:
#         return ["Configure a GEMINI_API_KEY para habilitar esta função."]

#     prompt = (
#         f"Quebre a seguinte tarefa em exatamente 3 ou 4 passos sequenciais, "
#         f"curtos e fáceis de focar: '{titulo_tarefa}'. "
#         f"Escreva apenas os passos, um por linha, sem introduções ou numeração manual."
#     )
    
#     system_instruction = (
#         "Você é um especialista em produtividade para neurodivergentes. "
#         "Crie checklists limpos, com verbos de ação claros e livres de poluição textual."
#     )

#     try:
#         response = client.models.generate_content(
#             model=MODELO_GEMINI,
#             contents=prompt,
#             config=types.GenerateContentConfig(
#                 system_instruction=system_instruction,
#                 temperature=0.2,
#             ),
#         )
        
#         # Limpa e filtra linhas vazias
#         passos = [linha.strip() for linha in response.text.split("\n") if linha.strip()]
        
#         # Remove marcadores comuns caso o modelo acabe gerando por teimosia (ex: "-", "*", "1.")
#         passos_limpos = []
#         for p in passos:
#             p_limpo = p.lstrip("0123456789.-* ")
#             if p_limpo:
#                 passos_limpos.append(p_limpo)
                
#         return passos_limpos

#     except Exception as e:
#         return [f"Não foi possível gerar os passos: {str(e)}"]