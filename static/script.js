let userName = "";

document.addEventListener("DOMContentLoaded", () => {
    addMessage("Diagbot", "Seja Bem-Vindo! Sou o Chatbot e estou aqui para ajudar. Qual é o seu nome?", "bot-message");
});

async function sendMessage(userInput = null) {
    const inputField = document.getElementById("user-input");

    if (!userInput) {
        userInput = inputField.value.trim();
        if (!userInput) return;
    }

    addMessage("Você", userInput, "user-message");
    inputField.value = "";

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userInput })
        });

        const data = await response.json();
        processBotResponse(data);
    } catch (error) {
        console.error("Erro:", error);
        addMessage("DiagBot", "Desculpe, ocorreu um erro. Tente novamente mais tarde.", "error-message");
    }
}

function processBotResponse(data) {
    if (!data.response) {
        addMessage("DiagBot", "Desculpe, não entendi sua mensagem.", "bot-message");
        return;
    }

    addMessage("DiagBot", data.response, "bot-message");

    if (data.note) {
        addMessage("DiagBot", data.note, "note-message");
    }

    if (data.end_chat) {
        setTimeout(addRestartButton, 2000);
        return;
    }

    if (data.ask_more) {
        setTimeout(() => {
            addMessage("DiagBot", "Gostaria de mais alguma coisa?", "bot-message");
            addYesNoButtons();
        }, 1000);
    }
}

function addMessage(sender, message, className) {
    const chatbox = document.getElementById("chatbox");

    if (!chatbox) return;

    const messageContainer = document.createElement("div");
    messageContainer.classList.add("message", className);
    messageContainer.innerHTML = `<p><strong>${sender}:</strong> ${message}</p>`;

    chatbox.appendChild(messageContainer);
    chatbox.scrollTop = chatbox.scrollHeight;
}

function addYesNoButtons() {
    removeElementById("yes-no-buttons");

    const chatbox = document.getElementById("chatbox");
    const buttonContainer = document.createElement("div");
    buttonContainer.id = "yes-no-buttons";
    buttonContainer.classList.add("button-container");

    const yesButton = document.createElement("button");
    yesButton.innerText = "Sim";
    yesButton.classList.add("yes-btn");
    yesButton.onclick = () => sendMessage("Sim");

    const noButton = document.createElement("button");
    noButton.innerText = "Não";
    noButton.classList.add("no-btn");
    noButton.onclick = () => {
        addMessage("Você", "Não", "user-message");
        setTimeout(endChat, 500);
    };

    buttonContainer.appendChild(yesButton);
    buttonContainer.appendChild(noButton);
    chatbox.appendChild(buttonContainer);
}

function endChat() {
    addMessage("DiagBot", "Ok! Se precisar de algo no futuro, estarei aqui. Tenha um ótimo dia!", "bot-message");
    setTimeout(addRestartButton, 2000);
}

function addRestartButton() {
    removeElementById("button-container");

    const chatbox = document.getElementById("chatbox");
    const restartButtonContainer = document.createElement("div");
    restartButtonContainer.id = "button-container";

    const restartButton = document.createElement("button");
    restartButton.classList.add("restart-btn");
    restartButton.innerText = "Reiniciar conversa";
    restartButton.onclick = () => location.reload();

    restartButtonContainer.appendChild(restartButton);
    chatbox.appendChild(restartButtonContainer);
}

function removeElementById(elementId) {
    const element = document.getElementById(elementId);
    if (element) element.remove();
}

document.addEventListener("DOMContentLoaded", () => {
    const themeToggleButton = document.getElementById("theme-toggle");
    const body = document.body;

  
    if (localStorage.getItem("theme") === "dark") {
        body.classList.add("dark-mode");
        themeToggleButton.innerText = "☀️ Modo Claro";
    }

    themeToggleButton.addEventListener("click", () => {
        body.classList.toggle("dark-mode");

        if (body.classList.contains("dark-mode")) {
            themeToggleButton.innerText = "☀️ Modo Claro";
            localStorage.setItem("theme", "dark");
        } else {
            themeToggleButton.innerText = "🌙 Modo Escuro";
            localStorage.setItem("theme", "light");
        }
    });
});

document.getElementById("user-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault(); 
        sendMessage();
    }
});