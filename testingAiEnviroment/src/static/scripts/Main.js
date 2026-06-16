// ---------------------------------------------------------------------------
// Utilitários de texto
// ---------------------------------------------------------------------------
function escapeHtml(texto) {
    return texto
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function formatarMensagemBot(texto) {
    const seguro = escapeHtml(texto);
    const comLinks = seguro.replace(
        /(https?:\/\/[^\s<]+)/g,
        '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
    );
    const comEstrelas = comLinks.replace(
        /⭐/g,
        '<span style="color: gold; font-size: 1.2em;">★</span>'
    );
    return comEstrelas.replace(/\n/g, "<br>");
}

// ---------------------------------------------------------------------------
// DOM helpers
// ---------------------------------------------------------------------------
function adicionarMensagem(remetente, texto, classe) {
    const chat = document.getElementById("chat");
    const conteudo = classe === "bot-msg" ? formatarMensagemBot(texto) : escapeHtml(texto);
    const msgHtml = `<div class="msg ${classe}"><strong>${remetente}</strong><br>${conteudo}</div>`;
    chat.innerHTML += msgHtml;
    chat.scrollTop = chat.scrollHeight;
    return chat.lastElementChild; // retorna o elemento criado
}

function criarBolhaBot() {
    const chat = document.getElementById("chat");
    const el = document.createElement("div");
    el.className = "msg bot-msg";
    el.innerHTML = `<strong>IPÊZINHO</strong><br><span class="stream-content"></span>`;
    chat.appendChild(el);
    chat.scrollTop = chat.scrollHeight;
    return el.querySelector(".stream-content");
}

function enviar() {
    const input  = document.getElementById("msg");
    const loader = document.querySelector(".loader");
    const texto  = input.value.trim();

    if (!texto) return;

    input.value = "";
    input.disabled = true;
    adicionarMensagem("Você", texto, "user-msg");
    loader.classList.add("active");

    // Cria a bolha do bot vazia — tokens aparecem conforme chegam
    const streamSpan = criarBolhaBot();
    let textoAcumulado = "";

    fetch("/chatbot/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensagem: texto }),
    })
    .then(response => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        function lerChunk() {
            return reader.read().then(({ done, value }) => {
                if (done) return;

                buffer += decoder.decode(value, { stream: true });

                // SSE: cada evento é "data: ...\n\n"
                const linhas = buffer.split("\n\n");
                buffer = linhas.pop(); // guarda fragmento incompleto

                for (const linha of linhas) {
                    if (!linha.startsWith("data:")) continue;
                    const payload = linha.slice(5).trim();
                    if (payload === "[DONE]") return;

                    try {
                        const { token } = JSON.parse(payload);
                        textoAcumulado += token;
                        // Renderiza com formatação a cada token
                        streamSpan.innerHTML = formatarMensagemBot(textoAcumulado);
                        document.getElementById("chat").scrollTop =
                            document.getElementById("chat").scrollHeight;
                    } catch (_) { /* ignora JSON malformado */ }
                }

                return lerChunk();
            });
        }

        return lerChunk();
    })
    .catch(() => {
        streamSpan.innerHTML = "Erro ao conectar com o servidor.";
    })
    .finally(() => {
        loader.classList.remove("active");
        input.disabled = false;
        input.focus();
    });
}

document.getElementById("msg").addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();
        enviar();
    }
});


function abrirMenuAcessibilidade() {
    document.getElementById("menu-acessibilidade").style.display = "block";
}

function fecharMenuAcessibilidade() {
    document.getElementById("menu-acessibilidade").style.display = "none";
}

function trocarTema() {
    const link = document.getElementById("theme");
    const atual = link.getAttribute("href");
    if (atual.includes("test.css")) {
        link.href = atual.replace("test.css", "test-contrast.css");
    } else {
        link.href = atual.replace("test-contrast.css", "test.css");
    }
}

adicionarMensagem(
    "IPÊZINHO",
    "Olá! Eu sou o IPÊZINHO, assistente virtual do CIAR UFG! 💚\n\nNeste canal irei te ajudar com diversos serviços como suporte em geral, abertura de sala, cadastramento de usuários, agendamento de reuniões e muito mais.",
    "bot-msg"
);