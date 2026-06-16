from flask import Flask, request, jsonify, render_template, Response, stream_with_context
from ollama import chat
from pathlib import Path
import chromadb
import json
import re

app = Flask(__name__)


CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "ipezinho"
CONTEXTO_PATH = "Contexto.md"

def _build_collection(collection, texto: str):
    """Divide o markdown por seções (##) e indexa cada uma."""
    raw_chunks = re.split(r"\n(?=## )", texto)
    chunks = [c.strip() for c in raw_chunks if c.strip()]
    if not chunks:
        chunks = [texto.strip()]

    collection.add(
        documents=chunks,
        ids=[f"chunk_{i}" for i in range(len(chunks))],
    )
    print(f"[RAG] {len(chunks)} chunks indexados.")

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# Reusa a coleção existente ou cria e indexa
existing = [c.name for c in chroma_client.list_collections()]
if COLLECTION_NAME in existing:
    collection = chroma_client.get_collection(COLLECTION_NAME)
    print(f"[RAG] Coleção '{COLLECTION_NAME}' carregada ({collection.count()} chunks).")
else:
    collection = chroma_client.create_collection(COLLECTION_NAME)
    texto_completo = Path(CONTEXTO_PATH).read_text(encoding="utf-8")
    _build_collection(collection, texto_completo)

SYSTEM_PROMPT = (
    "Você é o Ipêzinho, assistente virtual de suporte do CIAR/UFG, especializado no Moodle IPÊ. "
    "Responda sempre em português, de forma educada, objetiva e didática. "                         
    "Use exclusivamente as informações do contexto fornecido. "
    "Se não encontrar a resposta no contexto diga que esta sendo treinado diariamente e ainda não sabe responder, oriente o usuário a abrir um chamado em https://suporte.ciar.ufg.br/open.php. "
    "Respostas com no máximo 400 caracteres."
)

@app.route("/")
def index():
    return render_template("test.html")


@app.route("/chatbot/chat", methods=["POST"])
def chatbot():
    dados = request.get_json(silent=True) or {}
    pergunta = dados.get("mensagem", "").strip()

    if not pergunta:
        return jsonify({"resposta": "Mensagem vazia."})

    # 1. Busca os 3 chunks mais relevantes para a pergunta
    results = collection.query(query_texts=[pergunta], n_results=3)
    contexto_reduzido = "\n\n---\n\n".join(results["documents"][0])

    # 2. Monta as mensagens com contexto enxuto
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"[CONTEXTO RELEVANTE]\n{contexto_reduzido}\n\n"
                f"[PERGUNTA]\n{pergunta}"
            ),
        },
    ]

    # 3. Streaming — envia tokens conforme chegam (SSE)
    def gerar():
        try:
            stream = chat(
                model="gemma3:1b",
                messages=messages,
                stream=True,
            )
            for chunk in stream:
                token = chunk.message.content
                if token:
                    payload = json.dumps({"token": token}, ensure_ascii=False)
                    yield f"data: {payload}\n\n"
        except Exception as e:
            erro = json.dumps({"token": f"\n\n[Erro interno: {e}]"}, ensure_ascii=False)
            yield f"data: {erro}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return Response(
        stream_with_context(gerar()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no", 
        },
    )

if __name__ == "__main__":
    app.run(debug=True)