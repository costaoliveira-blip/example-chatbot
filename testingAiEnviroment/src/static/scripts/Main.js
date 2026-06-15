function escapeHtml(texto) {
    return texto
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
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

function adicionarMensagem(remetente, texto, classe) {
    const chat = document.getElementById("chat");
    const conteudo = classe === "bot-msg" ? formatarMensagemBot(texto) : escapeHtml(texto);
    const msgHtml = `<div class="msg ${classe}"><strong>${remetente}</strong><br>${conteudo}</div>`;
    chat.innerHTML += msgHtml;
    chat.scrollTop = chat.scrollHeight;
}

function enviar() {
    const input = document.getElementById("msg");
    const loader = document.querySelector(".loader");
    const texto = input.value.trim();

    if (!texto) return;

    input.value = "";
    adicionarMensagem("Você", texto, "user-msg");

    // Mostra o loader
    loader.classList.add("active");
    input.disabled = true;

    fetch("/chatbot/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensagem: texto })
    })
    .then(r => r.json())
    .then(d => {
        adicionarMensagem("Ipêzinho", d.resposta || "Sem resposta no momento.", "bot-msg");
    })
    .catch(() => {
        adicionarMensagem("Ipêzinho", "Erro ao conectar com o servidor.", "bot-msg");
    })
    .finally(() => {
        // Esconde o loader
        loader.classList.remove("active");
        input.disabled = false;
        input.focus();
    });
}

document.getElementById("msg").addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        enviar();
    }
});

adicionarMensagem(
    "IPÊZINHO",
    "Olá! Eu sou o IPÊZINHO, assistente virtual do CIAR UFG! 💚\n\nNeste canal irei te ajudar com diversos serviços como suporte em geral, abertura de sala, cadastramento de usuários, agendamento de reuniões e muito mais.",
    "bot-msg"
);


/*const document = getElementById("intput-user")
formatText --> send text to python llm
python llm return content --]> formatContentHtml
--> print on screen
*/
