#rodar esse script antes de qualquer coisa
#python chatProcessDb.py --pre-humanizar
import sqlite3
import re
from flask import Flask, Response, request, jsonify, render_template, stream_with_context
from ollama import chat
import os
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

# Estados que não permitem "0" — digitar 0 deve avisar o usuário
ESTADOS_SEM_VOLTAR = {
    "inicio", "perfil", "menu_docente", "menu_discente",
    "feedback", "feedback_estrelas", "feedback_mensagem", "feedback_fim",
    "coletar_nome", "coletar_email", "coletar_cpf", "coletar_descricao",
    "confirmar_dados",
}

# Mapeamento de texto livre → número da opção, por estado
TEXTO_PARA_OPCAO = {
    "perfil": {
        "professor": "1", "docente": "1",
        "técnico": "2", "tecnico": "2",
        "tutor": "3",
        "aluno": "4", "estudante": "4", "discente": "4",
    },
    "menu_docente": {
        "abrir sala": "1", "criar sala": "1", "sala": "1",
        "cadastrar": "2", "cadastro": "2", "usuarios": "2", "usuários": "2",
        "reunião": "3", "reuniao": "3", "agendar": "3",
        "suporte": "4", "ajuda": "4", "problema": "4",
    },
    "menu_discente": {
        "senha": "1", "login": "1", "acesso": "1",
        "site": "2", "não abre": "2", "nao abre": "2",
        "email": "3", "e-mail": "3", "recuperação": "3",
        "ticket": "4", "chamado": "4", "acompanhar": "4",
        "navegar": "5", "interface": "5", "moodle": "5",
        "perfil": "6", "dados": "6", "atualizar": "6",
        "cursos": "7", "curso": "7",
        "outro": "8", "outros": "8", "diferente": "8",
    },
    "criacao_sala_plataforma": {
        "ensino": "1",
        "pesquisa": "2", "extensão": "2", "extensao": "2",
    },
    "cadastro_usuarios_plataforma": {
        "ensino": "1",
        "pesquisa": "2", "extensão": "2", "extensao": "2",
    },
    "senha_plataforma": {
        "ensino": "1",
        "pesquisa": "2", "extensão": "2", "extensao": "2",
    },
    "senha_ensino_login_unico": {
        "não": "1", "nao": "1",
        "sim": "2", "não funcionou": "2", "nao funcionou": "2",
    },
    "senha_pesquisa_cpf": {
        "não": "1", "nao": "1",
        "sim": "2", "não funcionou": "2", "nao funcionou": "2",
    },
    "outro_problema": {
        "abrir": "1", "chamado": "1", "ticket": "1", "sim": "1",
    },
    "feedback": {
        "sim": "1", "quero": "1",
        "não": "2", "nao": "2", "não quero": "2", "nao quero": "2",
        "finalizar": "2", "sair": "2",
    },
}

SYSTEM_PROMPT_CLASSIFICADOR = f"""Você é um classificador de intenção do chat Ipêzinho (CIAR/UFG).
Responda SEMPRE em português do Brasil. Nunca responda em inglês ou em outro idioma.
Retorne APENAS um dos estados abaixo, sem nenhum texto adicional, sem pontuação extra:
{", ".join(sorted(ESTADOS_VALIDOS))}

REGRAS:
- Analise a mensagem do usuário e o estado atual.
- Retorne o estado mais adequado para a intenção descrita.
- Nunca retorne nada além de um estado válido da lista acima.
- Se não tiver certeza, retorne: perfil
- Responda em português do Brasil (pt-br), mesmo que a mensagem do usuário esteja em outro idioma.
"""

SYSTEM_PROMPT_HUMANIZADOR = """Você é o Ipêzinho, assistente de suporte do CIAR/UFG. Sua tarefa é reformular mensagens de orientação técnica para um tom mais humano, amigável e acolhedor, como se estivesse conversando com o usuário pessoalmente.
Responda SEMPRE em português do Brasil. Nunca responda em inglês ou em outro idioma.

REGRAS OBRIGATÓRIAS:
1. Preserve TODOS os links (URLs) exatamente como estão — nunca os modifique ou remova.
2. Preserve TODOS os números de opções (ex: "1 - Algo", "2 - Outro", "0 - Voltar") exatamente como estão, incluindo a opção "0".
3. Preserve instruções técnicas (nomes de campos, senhas, caminhos) sem alterar.
4. Apenas reformule o tom: torne mais cordial, empático e natural e mantenha a formalidade de um assistente institucional.
5. Não adicione informações que não estão no texto original.
6. Não encurte demais — mantenha todas as informações presentes.
7. Responda APENAS com o texto reformulado, sem explicações, e sempre em português do Brasil (pt-br).
"""

#Funçoes do banco de dados
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
    
def converter_youtube_embeded(url: str):
    if not url:
        return None
    
    m = re.search(r"[?&]v=([^&]+)", url)
    if m:
        return f"https://www.youtube.com/embed/{m.group(1)}"
    
    m = re.search(r"youtu\.be/([^?&]+)", url)
    if m:
        return f"https://www.youtube.com/embed/{m.group(1)}"
    return url

def buscar_link_tutorial(nome_tutorial: str):
    if not nome_tutorial:
        return None
    with get_db() as conn:
        row = conn.execute(
            "SELECT url FROM links WHERE nome_tutorial = ?",
            (nome_tutorial,)
        ).fetchone()

    if not row:
        return None
    
    return converter_youtube_embeded(row["url"])

def buscar_proximo_estado(estado_atual: str, opcao: str):
    opcao_str = str(opcao)
    with get_db() as conn:
        row = conn.execute(
            "SELECT estado_destino FROM opcoes WHERE estado_origem = ? AND opcao = ?",
            (estado_atual, opcao_str)
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

def estado_tem_voltar(estado: str) -> bool:
    """Verifica se o estado possui a opção '0' cadastrada no banco"""
    with get_db() as conn:
        row = conn.execute(
            "SELECT 1 FROM opcoes WHERE estado_origem = ? AND opcao = '0'",
            (estado,)
        ).fetchone()
    return row is not None

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

#Funções da Inteligencia Artificial

def classificar_intencao(mensagem: str, estado_atual: str) -> str:
    #Usa o modelo para classificar o que o usuario quer em um estado valido cadastrado
    try:
        resposta = chat(
            model="llama3:8b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_CLASSIFICADOR},
                {"role": "user", "content": (
                    f"Estado atual: {estado_atual}\n"
                    f"Mensagem do usuário: {mensagem}"
                )}
            ],
            stream=True,
            keep_alive="30m",
            options={"num_predict": 12, "temperature": 0}
        )

        partes = []
        for chunk in resposta:
            partes.append(chunk['message']['content'])
        texto_completo = "".join(partes)

        resultado = texto_completo.strip().lower().replace(" ", "_")
        resultado = resultado.split("\n")[0].split(",")[0].strip()
        print(f"[IA-CLASSIFICADOR] {estado_atual!r} + {mensagem!r} -> {resultado!r}")
        return resultado
    except Exception as e:
        print(f"[IA-CLASSIFICADOR] Erro: {e}")
        return ""
    

#Estados que nao passam por reformulação
ESTADOS_SEM_HUMANIZACAO = ESTADOS_COLETA | {
    "confirmar_dados", "feedback", "feedback_estrelas", "feedback_mensagem",
    "feedback_fim", "inicio", "abrir_ticket", "perfil"
}

def humanizar_mensagem(mensagem_banco: str, estado: str) -> str:
    """
    Versão humanizada sem chamar IA (otimiza o tempo de resposta)
    """

    if estado in ESTADOS_SEM_HUMANIZACAO:
        return mensagem_banco
    
    with get_db() as conn:
        row = conn.execute(
            "SELECT mensagem_humanizada from estados WHERE estado = ?", (estado,)
        ).fetchone()

    if row and row["mensagem_humanizada"]:
        return row["mensagem_humanizada"]
    
    return mensagem_banco

def _humanizar_via_ia(mensagem_banco: str, estado: str) -> str:
    try:
        resposta = chat(
            model="llama3:8b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_HUMANIZADOR},
                {"role": "user", "content": mensagem_banco}
            ],
            keep_alive="30m",
        )

        resultado = resposta.message.content.strip()
        print(f"[IA-HUMANIZADOR] {estado!r} -> reformulado OK")
        return resultado
    except Exception as e:
        print(f"[IA-HUMANIZADOR] Erro: {e} - usar mensagem original")
        return mensagem_banco
    
def _coluna_existe(conn, tabela: str, coluna: str) -> bool:
    info = conn.execute(f"PRAGMA table_info({tabela})").fetchall()
    return any(c["name"] == coluna for c in info)

def pre_humanizar_estados():
    with get_db() as conn:
        if not _coluna_existe(conn, "estados", "mensagem_humanizada"):
            conn.execute("ALTER TABLE estados ADD COLUMN mensagem_humanizada TEXT")
            conn.commit()

        rows = conn.execute("SELECT estado, mensagem FROM estados").fetchall()
        for row in rows:
            estado, mensagem = row["estado"], row["mensagem"]
            if estado in ESTADOS_SEM_HUMANIZACAO or not mensagem:
                continue
            humanizada = _humanizar_via_ia(mensagem, estado)
            conn.execute(
                "UPDATE estados SET mensagem_humanizada = ? WHERE estado = ?",
                (humanizada, estado)
            )
            conn.commit()
        print("Pré-Humanizacao concluida")

#Helpers para texto
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

def _inejtar_rodape_voltar(mensagem: str, estado: str) -> str:
    """Injeta o '0 - Voltar' apenas se o estado tem opcao de voltar no banco"""

    mensagem_limpa = re.sub(
        r'\n?[•\-]?\s*0[\.\-\s]+[Vv]oltar[^\n]*', '', mensagem
    ).rstrip()

    if estado_tem_voltar(estado):
        return mensagem_limpa + "\n\n0 - Voltar"
    return mensagem_limpa

#Principais processamentos

def processar_mensagem(mensagem: str, estado_atual: str, dados_coleta: dict) -> dict:
    
    def montar_resposta(estado_destino: str, extra_msg: str = None) -> dict:
        msg_banco, link_nome = buscar_estado(estado_destino)
        msg_humanizada = humanizar_mensagem(msg_banco, estado_destino)
        msg_final = _inejtar_rodape_voltar(msg_humanizada, estado_destino)

        if extra_msg:
            msg_final = extra_msg + "\n\n" + msg_final
        return {
            "estado": estado_destino,
            "resposta": msg_final,
            "link_tutorial": buscar_link_tutorial(link_nome),
            "dados_coleta": dados_coleta,
        }
    
    def reexibir(aviso: str = None) -> dict:
        msg_banco, link_nome = buscar_estado(estado_atual)
        msg_humanizada = humanizar_mensagem(msg_banco, estado_atual)
        msg_final = _inejtar_rodape_voltar(msg_humanizada, estado_atual)
        if aviso:
            msg_final = aviso + "\n\n" + msg_final
        return {
            "estado": estado_atual,
            "resposta": msg_final,
            "link_tutorial": buscar_link_tutorial(link_nome),
            "dados_coleta": dados_coleta,
        }
    
    #0 - Voltar
    if mensagem.strip() == "0":
        if estado_tem_voltar(estado_atual):
            return montar_resposta(buscar_proximo_estado(estado_atual, "0"))
        else:
            aviso = (
                "Você já está no início do atendimento."
                if estado_atual in {"inicio", "perfil"}
                else  "Não é possível voltar nesta etapa."
            )
            return reexibir(aviso)
        
    #Coleta de dados

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
            return {
                "estado": proximo,
                "resposta": msg_confirmacao,
                "link_tutorial": None,
                "dados_coleta": dados_coleta,
            }
        return montar_resposta(proximo)
    
    if estado_atual == "feedback_estrelas":
        estrelas_map = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5}
        valor = mensagem.strip()
        if valor not in estrelas_map: 
            return reexibir("Por favor, digite um numero de 1 a 5:")
        dados_coleta["estrelas"] = estrelas_map[valor]
        return montar_resposta(buscar_proximo_estado(estado_atual, valor))
    
    #Mensagem do feedback
    if estado_atual == "feedback_mensagem":
        comentario = None if mensagem.strip() == "1" else mensagem
        salvar_avaliacao(dados_coleta.get("estrelas", 3), comentario)
        dados_coleta = {}
        return montar_resposta(buscar_proximo_estado(estado_atual, "*"))
    
    #Confirmar dados
    if estado_atual == "confirmar_dados":
        v = mensagem.strip()
        if v == "1":
            print(f"[TICKET] {dados_coleta}")
            dados_coleta_salvo = dict(dados_coleta)
            dados_coleta = {}
            msg_banco, link_nome = buscar_estado("feedback")
            msg_humanizada = humanizar_mensagem(msg_banco, "feedback")
            msg_final = _inejtar_rodape_voltar(msg_humanizada, "feedback")
            return {
                "estado": "feedback",
                "resposta": "Chamado aberto com sucesso!\n\n" + msg_final,
                "link_tutorial": buscar_link_tutorial(link_nome),
                "dados_coleta": dados_coleta,
            }
        elif v == "2":
            return montar_resposta("coletar_nome")
        else:
            return reexibir("Digite 1 para confirmar ou 2 para corrigir.")
    
    opcoes = listar_opcoes(estado_atual)
    if not opcoes:
        return reexibir("Não entendi. Por favor, escolha uma das opções:")
    
    if opcoes == ["*"]:
        return montar_resposta(buscar_proximo_estado(estado_atual, "*"))
    
    numeros_validos = [o for o in opcoes if o not in ("*", "0")]

    if re.fullmatch(r"\d+", mensagem.strip()):
        numero = mensagem.strip()
        if numero in numeros_validos:
            return montar_resposta(buscar_proximo_estado(estado_atual, numero))
        return reexibir(f"Opção '{numero}' inválida. Escolha uma das opções:")

    opcao_por_texto = match_texto_opcao(mensagem, estado_atual)
    if opcao_por_texto and opcao_por_texto in numeros_validos:
        print(f"[MATCH] {estado_atual!r} + {mensagem!r} -> opção {opcao_por_texto!r}")
        return montar_resposta(buscar_proximo_estado(estado_atual, opcao_por_texto))
    
    #Fallback do modelo
    if estado_atual not in ESTADOS_SO_NUMERICO:
        resultado_ia = classificar_intencao(mensagem, estado_atual)
        if resultado_ia in ESTADOS_VALIDOS:
            return montar_resposta(resultado_ia)
    return reexibir("Não entendi. Por favor, escolha uma das opções:")

#Rotas

@app.route("/")
def index():
    return render_template("test.html")

@app.route("/chatbot/chat", methods=["POST"])
def chatbot():
    payload = request.get_json(silent=True) or {}

    mensagem = payload.get("mensagem", "").strip()
    estado = payload.get("estado", "inicio")
    dados = payload.get("dados_coleta", {})

    if not mensagem:
        return jsonify({
            "resposta": "Mensagem vazia.",
            "estado": estado,
            "link_tutorial": None,
            "dados_coleta": dados,
        })

    resultado = processar_mensagem(mensagem, estado, dados)

    return jsonify(resultado)

if __name__ == "__main__":
    import sys
    if "--pre-humanizar" in sys.argv:
        pre_humanizar_estados()
    else:
        app.run(debug=True)
