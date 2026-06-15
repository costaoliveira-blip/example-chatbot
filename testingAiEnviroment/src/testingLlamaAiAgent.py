from flask import Flask, request, jsonify, render_template
from ollama import chat, ChatResponse
from pathlib import Path

app = Flask(__name__)

contexto = Path("Contexto.md").read_text(encoding="utf-8")

@app.route("/")
def index():
    return render_template("test.html")  # seu test.html renomeado

@app.route("/chatbot/chat", methods=["POST"])
def chatbot():
    dados = request.get_json()
    pergunta = dados.get("mensagem", "").strip()

    if not pergunta:
        return jsonify({"resposta": "Mensagem vazia."})

    response = chat(model="medgemma", messages=[
        {
            "role": "system",
            "content": (
                "Você é um assistente com restrito ao contexto. Sua única tarefa é responder "
                "à pergunta do usuário baseando-se prioritariamente nas informações fornecidas referentes ao moodle ipe da Universidade Federal de Goiás "
                "no contexto dos arquivos. Caso não encontre no contexto, informe que não foi "
                "encontrado e tente ajudar da melhor forma possível, utilizando seus parametros. "
                "Limite de no máximo 350 caracteres."
            )
        },
        {
            "role": "user",
            "content": f"[CONTEXTO DOS ARQUIVOS]\n{contexto}\n\n[PERGUNTA]\n{pergunta}"
        }
    ])
    total_sec = response.total_duration / 1000000000
    print(total_sec)
    return jsonify({"resposta": response.message.content})

if __name__ == "__main__":
    app.run(debug=True)
