import sqlite3
import re
from flask import Flask, request, jsonify, render_template
from ollama import chat

app = Flask(__name__)

DB_PATH = "database.db"

ESTADOS_VALIDOS = {
    "inicio", "perfil", "menu_docente", "menu_discente",
    "criacao_sala_plataforma", "criacao_sala_ensino", "criacao_sala_pesquisa",
    "cadastro_usuarios_plataforma", "cadastro_usuarios_ensino", "cadastro_usuarios_pesquisa",
    "agendar_reuniao",
    "senha_plataforma", "senha_ensino_login_unico", "senha_ensino_orienta_login_unico",
    "senha_ticket_orienta_ensino", "senha_pesquisa_cpf", "senha_pesquisa_orienta_cpf",
    "senha_ticket_orienta_pesquisa",
    "site_nao_abrindo", "problemas_email_recuperacao", "acompanhar_ticket",
    "navegar_pela_interface_moodle", "atualizar_dados_perfil", "acessar_cursos",
    "outro_problema", "coletar_nome", "coletar_email", "coletar_cpf",
    "coletar_descricao", "confirmar_dados", "abrir_ticket",
    "feedback", "feedback_estrelas", "feedback_mensagem", "feedback_fim",
}

ESTADOS_COLETA = {"coletar_nome", "coletar_email", "coletar_cpf", "coletar_descricao"}

# Estados onde texto livre NÃO deve acionar a IA — só aceita número
ESTADOS_SO_NUMERICO = {
    "feedback_estrelas",
    "feedback",
    "confirmar_dados",
}

# Mapeamento de texto livre → número da opção, por estado
# Permite que o usuário digite palavras em vez do número
TEXTO_PARA_OPCAO = {
    "perfil": {
        "professor": "1",
        "docente": "1",
        "técnico": "2",
        "tecnico": "2",
        "tutor": "3",
        "aluno": "4",
        "estudante": "4",
        "discente": "4",
    },
    "menu_docente": {
        "abrir sala": "1",
        "criar sala": "1",
        "sala": "1",
        "cadastrar": "2",
        "cadastro": "2",
        "usuarios": "2",
        "usuários": "2",
        "reunião": "3",
        "reuniao": "3",
        "agendar": "3",
        "suporte": "4",
        "ajuda": "4",
        "problema": "4",
    },
    "menu_discente": {
        "senha": "1",
        "login": "1",
        "acesso": "1",
        "site": "2",
        "não abre": "2",
        "nao abre": "2",
        "email": "3",
        "e-mail": "3",
        "recuperação": "3",
        "ticket": "4",
        "chamado": "4",
        "acompanhar": "4",
        "navegar": "5",
        "interface": "5",
        "moodle": "5",
        "perfil": "6",
        "dados": "6",
        "atualizar": "6",
        "cursos": "7",
        "curso": "7",
        "outro": "8",
        "outros": "8",
        "diferente": "8",
    },
    "criacao_sala_plataforma": {
        "ensino": "1",
        "pesquisa": "2",
        "extensão": "2",
        "extensao": "2",
    },
    "cadastro_usuarios_plataforma": {
        "ensino": "1",
        "pesquisa": "2",
        "extensão": "2",
        "extensao": "2",
    },
    "senha_plataforma": {
        "ensino": "1",
        "pesquisa": "2",
        "extensão": "2",
        "extensao": "2",
    },
    "senha_ensino_login_unico": {
        "não": "1",
        "nao": "1",
        "sim": "2",
        "não funcionou": "2",
        "nao funcionou": "2",
    },
    "senha_pesquisa_cpf": {
        "não": "1",
        "nao": "1",
        "sim": "2",
        "não funcionou": "2",
        "nao funcionou": "2",
    },
    "outro_problema": {
        "abrir": "1",
        "chamado": "1",
        "ticket": "1",
        "sim": "1",
    },
    "feedback": {
        "sim": "1",
        "quero": "1",
        "não": "2",
        "nao": "2",
        "não quero": "2",
        "nao quero": "2",
        "finalizar": "2",
        "sair": "2",
    },
}

SYSTEM_PROMPT = f"""Você é um classificador de intenção do chat Ipêzinho (CIAR/UFG).
Retorne apenas um dos estados abaixo, sem nenhum texto adicional:
{", ".join(ESTADOS_VALIDOS)}

REGRAS:
- Analise a mensagem do usuário e o estado atual
- Retorne o estados mais adequado para a intenção descrita
- Nunca retorne nada além de um estado válido da lista
- Se você nao tiver certeza, retorne "perfil"Ellipsis
"""


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def buscar_estado(estado: str):
    with get_db() as conn:
        row = conn.execute(
            "SELECT mensagem, link_tutorial FROM estados WHERE estado = ?", (estado,)
        ).fetchone()
        if row:
            return row["mensagem"], row["link_tutorial"]
        return "Não entendi. Digite qualquer coisa para reiniciar.", None
    
def buscar_link_tutorial(nome_tutorial: str):
    if not nome_tutorial:
        return None
    with get_db() as conn:
        row = conn.execute(
            "SELECT url FROM links WHERE nome_tutorial = ?", (nome_tutorial,)
        ).fetchone()
    return row["url"] if row else None

def buscar_proximo_estado(estado_atual: str, opcao: str):
    with get_db() as conn:
        row = conn.execute(
            "SELECT estado_destino FROM opcoes WHERE estado_origem = ? AND opcao = ?",
            (estado_atual, opcao)
        ).fetchone()
        if row:
            return row["estado_destino"]
        row = conn.execute(
            "SELECT estado_destino FROM opcoes WHERE estado_origem = ? AND opcao = '*'",
            (estado_atual,)
        ).fetchone()
        if row:
            return row["estado_destino"]
    return "perfil"

def listar_opcoes(estado_atual: str):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT opcao FROM opcoes WHERE estado_origem = ?", (estado_atual,)
        ).fetchall()
    return [r["opcao"] for r in rows]

def salvar_avaliacao(estrelas: float, descricao: str = None):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO avaliacoes (estrelas_avaliacao, mensagem, descricao) VALUES (?, ?, ?)",
            (estrelas, f"{int(estrelas)} estrelas", descricao)
        )
        conn.commit()

def classificar_intencao(mensagem: str, estado_atual: str) -> str:
    try:
        resposta = chat (
            model="gemma3:1b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": (
                    f"Estado atual: {estado_atual}\n"
                    f"Mensagem do usuário: {mensagem}"
                )}
            ]
        )
        resultado = resposta.message.content.strip().lower().replace(" ", "_")
        print(f"[IA] {estado_atual!r} + {mensagem!r} → {resultado!r}")
        return resultado
    except Exception as e:
        print(f"[IA] Erro: {e}")
        return ""
    
def match_texto_opcao(mensagem: str, estado_atual: str) -> str | None:
    mapa = TEXTO_PARA_OPCAO.get(estado_atual)
    if not mapa:
        return None
    msg_lower = mensagem.strip().lower()

    if msg_lower in mapa:
        return mapa[msg_lower]
    for chave, opcao in mapa.items():
        if chave in msg_lower:
            return opcao
    return None

def processar_mensagem(mensagem: str, estado_atual: str, dados_coleta: dict) -> dict:
    def responder(proximo, extra_msg=None):
        msg, link_nome = buscar_estado(proximo)
        link = buscar_link_tutorial(link_nome)
        return {
            "estado": proximo,
            "resposta": extra_msg + "\n\n" + msg if extra_msg else msg,
            "link_tutorial": link,
            "dados_coleta": dados_coleta,
        }
    
    def reexibir(aviso=None):
        msg, link_nome = buscar_estado(estado_atual)
        link = buscar_link_tutorial(link_nome)
        return {
            "estado": estado_atual,
            "resposta": aviso + "\n\n" + msg if aviso else msg,
            "link_tutorial": link,
            "dados_coleta": dados_coleta,
        }
    
    if estado_atual in ESTADOS_COLETA:
        campo_map = {
            "coletar_nome": "nome",
            "coletar_email": "email",
            "coletar_cpf": "cpf",
            "coletar_descricao": "descricao",
        }
        dados_coleta[campo_map[estado_atual]] = mensagem
        proximo = buscar_proximo_estado(estado_atual, "*")

        if proximo == "confirmar_dados":
            msg_confirmacao = (
                f"Confira os dados antes de abrir o chamado:\n\n"
                f"Nome: {dados_coleta.get('nome', '-')}\n"
                f"E-mail: {dados_coleta.get('email', '-')}\n"
                f"CPF: {dados_coleta.get('cpf', '-')}\n"
                f"Descrição: {dados_coleta.get('descricao', '-')}\n\n"
                f"1 - Confirmar e abrir chamado\n2 - Corrigir dados"
            )
            return {"estado": proximo, "resposta": msg_confirmacao,
                    "link_tutorial": None, "dados_coleta": dados_coleta}
        return responder(proximo)
    
    if estado_atual == "feedback_estrelas":
        estrelas_map = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5}
        valor = mensagem.strip()
        if valor not in estrelas_map:
            return reexibir("Por favor, digite um número de 1 a 5: ")
        dados_coleta["estrelas"] = estrelas_map[valor]
        proximo = buscar_proximo_estado(estado_atual, valor)
        return responder(proximo)
    
    if estado_atual == "feedback_mensagem":
        comentario = None if mensagem.strip() == "1" else mensagem
        salvar_avaliacao(dados_coleta.get("estrelas", 3), comentario)
        dados_coleta = {}
        return responder(buscar_proximo_estado(estado_atual, "*"))
    
    if estado_atual == "confirmar_dados":
        v = mensagem.strip()
        if v == "1":
            print(f"[TICKET] {dados_coleta}")
            dados_coleta = {}
            msg, link_nome = buscar_estado("feedback")
            return {"estado": "feedback",
                    "resposta": "Chamado aberto com sucesso!\n\n" + msg,
                    "link_tutorial": buscar_link_tutorial(link_nome),
                    "dados_coleta": dados_coleta}
        elif v == "2":
            return responder("coletar_nome")
        else:
            return reexibir("Digite 1 para confirmar ou 2 para corrigir.")
    opcoes = listar_opcoes(estado_atual)

    if not opcoes:
        return reexibir("Não entendi. Por favor, escolha uma das opções:")

    if opcoes == ["*"]:
        return responder(buscar_proximo_estado(estado_atual, "*"))
    
    numeros_validos = [o for o in opcoes if o not in ("*",)]
    
    if re.fullmatch(r"\d+", mensagem.strip()):
        numero = mensagem.strip()
        if numero in numeros_validos:
            return responder(buscar_proximo_estado(estado_atual, numero))
        return reexibir(f"Opção '{numero}' inválida. Escolha uma das opções:")
    
    opcao_por_texto = match_texto_opcao(mensagem, estado_atual)
    if opcao_por_texto and opcao_por_texto in numeros_validos:
        print(f"[MATCH] {estado_atual!r} + {mensagem!r} + opcao {opcao_por_texto!r}")
        return responder(buscar_proximo_estado(estado_atual, opcao_por_texto))
    
    if estado_atual not in ESTADOS_SO_NUMERICO:
        resultado_ia = classificar_intencao(mensagem, estado_atual)
        if resultado_ia in ESTADOS_VALIDOS:
            return responder(resultado_ia)
    
    return reexibir("Não entendi. Por favor, escolha uma das opções:")

@app.route("/")
def index():
    return render_template("test.html")

@app.route("/chatbot/chat", methods=["POST"])
def chatbot():
    payload = request.get_json(silent=True) or {}
    mensagem = payload.get("mensagem", "").strip()
    estado_atual = payload.get("estado", "inicio")
    dados_coleta = payload.get("dados_coleta", {})

    if not mensagem:
        return jsonify({"resposta": "Mensagem vazia.", "estado": estado_atual,
                        "link_tutorial": None, "dados_coleta": dados_coleta})
    
    resultado = processar_mensagem(mensagem, estado_atual, dados_coleta)
    return jsonify(resultado)


if __name__ == "__main__":
    app.run(debug=True)