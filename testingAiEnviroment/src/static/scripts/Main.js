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
    const conteudo = classe === "bot-msg" ? formatarMensagemBot(texto) : escapeHtml(texto);
    const msgHtml = `<div class="msg ${classe}"><strong>${remetente}</strong><br>${conteudo}</div>`;
    chat.innerHTML += msgHtml;
    chat.scrollTop = chat.scrollHeight;
}

function adicionarLinkTutorial(url) {
    if (!url) return;
    const chat = document.getElementById("chat");
    const msgHtml = `
        <div class="msg bot-msg tutorial-link">
            <strong>IPÊZINHO</strong><br>
            🎬 <iframe src="${escapeHtml(url)}" width="400" height="250" title="teste de titulo">
            </iframe>
        </div>`;
    chat.innerHTML += msgHtml;
    chat.scrollTop = chat.scrollHeight;
}


function enviar() {
    const input  = document.getElementById("msg");
    const loader = document.querySelector(".loader");
    const texto  = input.value.trim();

    if (!texto) return;

    input.value = "";
    input.disabled = true;
    loader.classList.add("active");

    adicionarMensagem("Você", texto, "user-msg");

    fetch("/chatbot/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            mensagem: texto,
            estado: estadoAtual,
            dados_coleta: dadosColeta,
        }),
    })
    .then(r => r.json())
    .then(d => {
        // Atualiza o estado da sessão
        estadoAtual = d.estado || "inicio";
        dadosColeta = d.dados_coleta || {};

        // Exibe a resposta do bot
        adicionarMensagem("IPÊZINHO", d.resposta || "Sem resposta no momento.", "bot-msg");

        // Exibe o link do tutorial se existir
        if (d.link_tutorial) {
            adicionarLinkTutorial(d.link_tutorial);
        }
    })
    .catch(() => {
        adicionarMensagem("IPÊZINHO", "Erro ao conectar com o servidor.", "bot-msg");
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
// Mensagem de boas-vindas (dispara o primeiro estado automaticamente)
// ---------------------------------------------------------------------------
adicionarMensagem(
    "IPÊZINHO",
    "Olá! Eu sou o IPÊZINHO, assistente virtual do CIAR UFG! 💚\n\nNeste canal irei te ajudar com diversos serviços como suporte em geral, abertura de sala, cadastramento de usuários, agendamento de reuniões e muito mais.\n\nDigite qualquer coisa para começar!",
    "bot-msg"
);