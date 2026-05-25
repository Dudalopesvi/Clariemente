import os
import re

# ---------------------------------------------------------------------------
# Tentativa de carregar o Gemini. Se a chave não estiver configurada,
# o sistema cai no modo offline com respostas estáticas.
# ---------------------------------------------------------------------------
try:
    from google import genai
    from google.genai import types as genai_types

    _API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
    _client = genai.Client(api_key=_API_KEY) if _API_KEY else None
except ImportError:
    _client = None

MODELO_GEMINI = "gemini-2.5-flash"

# RF04 – RN04: controle de última sugestão para evitar repetição consecutiva
_ultima_sugestao_sos: str = ""


# ---------------------------------------------------------------------------
# Personas de sistema por perfil TDAH (RF01 / RF03 / RF04)
# ---------------------------------------------------------------------------
_PERSONAS = {
    "desatento": (
        "Você é o ClariMente, assistente para estudantes com TDAH Desatento. "
        "Use etapas detalhadas e lembretes suaves. "
        "Frases curtas. Verbos no imperativo. Sem jargões."
    ),
    "hiperativo": (
        "Você é o ClariMente, assistente para estudantes com TDAH Hiperativo/Impulsivo. "
        "Ações rápidas com pausas frequentes. "
        "Frases curtíssimas. Ritmo acelerado. Sempre incentive."
    ),
    "combinado": (
        "Você é o ClariMente, assistente para estudantes com TDAH Combinado. "
        "Misture etapas detalhadas com ações rápidas e pausas. "
        "Linguagem positiva, direta e acolhedora."
    ),
}

_PERSONA_PADRAO = (
    "Você é o ClariMente, assistente de produtividade para estudantes com TDAH. "
    "Seja direto, positivo e use linguagem encorajadora."
)


def _persona(perfil_tdah: str) -> str:
    return _PERSONAS.get(perfil_tdah.lower().strip(), _PERSONA_PADRAO)


def _limpar_passos(texto: str) -> list:
    """Divide resposta em linhas e remove marcadores automáticos do modelo."""
    linhas = [l.strip() for l in texto.split("\n") if l.strip()]
    limpos = []
    for linha in linhas:
        linha_limpa = re.sub(r"^[\d\.\-\*\•]+\s*", "", linha).strip()
        if linha_limpa:
            limpos.append(linha_limpa)
    return limpos


# ---------------------------------------------------------------------------
# RF04 – Chatbot adaptável
# ---------------------------------------------------------------------------
def obter_resposta_ia(pergunta: str, perfil_tdah: str) -> list:
    """
    Responde a perguntas livres do usuário adaptando ao perfil TDAH.
    RN02 – Linguagem sempre positiva.
    RN03 – Tempo de resposta: tratado via Gemini Flash (modelo mais rápido).
    """
    if _client:
        try:
            resp = _client.models.generate_content(
                model=MODELO_GEMINI,
                contents=pergunta,
                config=genai_types.GenerateContentConfig(
                    system_instruction=_persona(perfil_tdah),
                    temperature=0.4,
                ),
            )
            return _limpar_passos(resp.text)
        except Exception as e:
            return [f"Erro ao conectar com a IA: {e}"]

    # Modo offline – respostas estáticas por perfil
    _respostas_offline = {
        "desatento": [
            "Respira fundo. Escolha UMA coisa para fazer agora.",
            "Abra o material que você vai usar.",
            "Faça apenas o primeiro passo. Um de cada vez.",
        ],
        "hiperativo": [
            "Para. Olha para a tarefa. Vai!",
            "5 minutos no relógio. Começa agora.",
            "Pausa de 2 minutos após terminar. Você consegue!",
        ],
        "combinado": [
            "Escolha a tarefa mais urgente.",
            "Divida em 3 passos rápidos.",
            "Você consegue! Um passo de cada vez.",
        ],
    }
    return _respostas_offline.get(
        perfil_tdah.lower(),
        ["Foque na menor ação possível para começar.", "Você consegue!"],
    )


# ---------------------------------------------------------------------------
# RF04 – Botão SOS "Tô Travado"
# ---------------------------------------------------------------------------
def sos_travado(tarefa_titulo: str, perfil_tdah: str) -> list:
    """
    RN01 – Simplifica a tarefa atual para uma ação de no máximo 5 minutos.
    RN04 – Varia a abordagem a cada acionamento (não repete a mesma sugestão).
    """
    global _ultima_sugestao_sos

    prompt = (
        f"O usuário está travado na tarefa '{tarefa_titulo}'. "
        f"Sugira UMA única ação de no máximo 5 minutos para destravar. "
        f"Não repita esta sugestão anterior: '{_ultima_sugestao_sos}'. "
        f"Responda com apenas 1 frase curta no imperativo. Sem introduções."
    )

    if _client:
        try:
            resp = _client.models.generate_content(
                model=MODELO_GEMINI,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    system_instruction=_persona(perfil_tdah),
                    temperature=0.9,  # Alta criatividade para variar sugestões
                ),
            )
            sugestao = resp.text.strip()
            _ultima_sugestao_sos = sugestao
            return ["🆘 SOS ATIVADO!", sugestao, "⏱ Foque só nisso por 5 minutos."]
        except Exception as e:
            return [f"Erro: {e}"]

    # Modo offline – pool rotativo de sugestões SOS
    _sugestoes_sos = [
        "Abra o caderno e escreva só o título da tarefa.",
        "Leia apenas a primeira linha do enunciado.",
        "Separe o material que você vai precisar.",
        "Escreva o que você JÁ sabe sobre o assunto.",
        "Faça 3 respirações profundas e comece com 1 palavra.",
    ]
    opcoes = [s for s in _sugestoes_sos if s != _ultima_sugestao_sos]
    import random
    sugestao = random.choice(opcoes) if opcoes else _sugestoes_sos[0]
    _ultima_sugestao_sos = sugestao
    return ["🆘 SOS ATIVADO!", sugestao, "⏱ Foque só nisso por 5 minutos."]


# ---------------------------------------------------------------------------
# RF03 – Quebra automática de tarefas em micro-etapas
# ---------------------------------------------------------------------------
def gerar_passos_tarefa(titulo_tarefa: str, perfil_tdah: str) -> list:
    """
    RN01 – Adapta etapas ao perfil TDAH.
    RN02 – Entre 2 e 7 micro-etapas.
    RN03 – Verbos no imperativo.
    RN04 – Duração estimada de 2 a 15 minutos por etapa.
    """
    prompt = (
        f"Quebre a tarefa '{titulo_tarefa}' em micro-etapas sequenciais. "
        f"Regras: mínimo 2, máximo 7 etapas. "
        f"Cada etapa: verbo no imperativo, duração de 2 a 15 minutos. "
        f"Escreva apenas as etapas, uma por linha, sem numeração."
    )

    perfil = perfil_tdah.lower().strip()
    if perfil == "desatento":
        prompt += " Etapas detalhadas com lembretes suaves."
    elif perfil == "hiperativo":
        prompt += " Ações rápidas com pausas de 2 min entre elas."
    else:
        prompt += " Mix equilibrado de detalhe e ritmo."

    if _client:
        try:
            resp = _client.models.generate_content(
                model=MODELO_GEMINI,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    system_instruction=_persona(perfil_tdah),
                    temperature=0.3,
                ),
            )
            passos = _limpar_passos(resp.text)
            # RN02 – garante limites de quantidade
            passos = passos[:7] if len(passos) > 7 else passos
            return passos if len(passos) >= 2 else passos + ["Revise o que foi feito."]
        except Exception as e:
            return [f"Erro ao gerar passos: {e}"]

    # Modo offline por perfil
    _passos_offline = {
        "desatento": [
            "Organize o espaço de trabalho retirando distrações.",
            "Leia o enunciado completo com atenção.",
            "Anote os pontos principais em tópicos.",
            "Execute a primeira parte por 10 minutos.",
            "Faça uma pausa de 5 minutos em silêncio.",
        ],
        "hiperativo": [
            "Separe só o material necessário.",
            "Faça o primeiro item por 5 minutos.",
            "Pause 2 minutos. Levante e beba água.",
            "Continue com o próximo item.",
        ],
        "combinado": [
            "Organize o espaço rapidamente.",
            "Execute a primeira metade por 15 minutos.",
            "Pausa de 5 minutos.",
            "Finalize a segunda metade.",
            "Revise o resultado.",
        ],
    }
    return _passos_offline.get(perfil, _passos_offline["combinado"])
