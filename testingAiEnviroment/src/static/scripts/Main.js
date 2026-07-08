// ---------------------------------------------------------------------------
// Estado da sessão — trafega entre frontend e backend
// ---------------------------------------------------------------------------
let estadoAtual = "inicio";
let dadosColeta = {};

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

    const div = document.createElement("div");
    div.className = `msg ${classe}`;

    div.innerHTML = `
        <strong>${remetente}</strong><br>
        <span class="conteudo"></span>
    `;

    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;

    const conteudo = div.querySelector(".conteudo");

    if (classe === "bot-msg") {
        conteudo.innerHTML = formatarMensagemBot(texto);
    } else {
        conteudo.innerHTML = escapeHtml(texto);
    }

    return conteudo;
}

// ---------------------------------------------------------------------------
// Efeito de digitação do bot
// ---------------------------------------------------------------------------
async function escreverMensagem(elemento, texto, velocidade = 16) {

    let atual = "";

    for (const letra of texto) {

        atual += letra;

        elemento.innerHTML = formatarMensagemBot(atual);

        const chat = document.getElementById("chat");
        chat.scrollTop = chat.scrollHeight;

        await new Promise(resolve => setTimeout(resolve, velocidade));
    }
}

function adicionarLinkTutorial(url) {

    if (!url) return;

    const chat = document.getElementById("chat");

    const msgHtml = `
        <div class="msg bot-msg tutorial-link">
            <strong>IPÊZINHO</strong><br>
            <iframe
                src="${escapeHtml(url)}"
                width="500"
                height="250"
                title="Tutorial">
            </iframe>
        </div>
    `;

    chat.innerHTML += msgHtml;
    chat.scrollTop = chat.scrollHeight;
}

// ---------------------------------------------------------------------------
// Envio de mensagens
// ---------------------------------------------------------------------------
async function enviar() {

    const input = document.getElementById("msg");
    const loader = document.querySelector(".loader");

    const texto = input.value.trim();

    if (!texto) return;

    input.value = "";
    input.disabled = true;

    loader.classList.add("active");

    adicionarMensagem("Você", texto, "user-msg");

    try {

        const response = await fetch("/chatbot/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                mensagem: texto,
                estado: estadoAtual,
                dados_coleta: dadosColeta

            })

        });

        const d = await response.json();

        estadoAtual = d.estado || "inicio";
        dadosColeta = d.dados_coleta || {};

        const elemento = adicionarMensagem(
            "IPÊZINHO",
            "",
            "bot-msg"
        );

        await escreverMensagem(
            elemento,
            d.resposta || "Sem resposta no momento."
        );

        if (d.link_tutorial) {
            adicionarLinkTutorial(d.link_tutorial);
        }

    } catch (e) {

        const elemento = adicionarMensagem(
            "IPÊZINHO",
            "",
            "bot-msg"
        );

        await escreverMensagem(
            elemento,
            "Erro ao conectar com o servidor."
        );

    } finally {

        loader.classList.remove("active");

        input.disabled = false;
        input.focus();

    }
}

// ---------------------------------------------------------------------------
// Enter envia mensagem
// ---------------------------------------------------------------------------
document.getElementById("msg").addEventListener("keydown", function (event) {

    if (event.key === "Enter") {

        event.preventDefault();
        enviar();

    }

});

// ---------------------------------------------------------------------------
// Acessibilidade
// ---------------------------------------------------------------------------
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

// ---------------------------------------------------------------------------
// Mensagem inicial
// ---------------------------------------------------------------------------
adicionarMensagem(
    "IPÊZINHO",
    "Olá! Eu sou o IPÊZINHO, assistente virtual do CIAR UFG! 💚\n\nNeste canal irei te ajudar com diversos serviços como suporte em geral, abertura de sala, cadastramento de usuários, agendamento de reuniões e muito mais.\n\nDigite qualquer coisa para começar!",
    "bot-msg"
);