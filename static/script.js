let userName = "";

// When the page loads, show the welcome message
document.addEventListener("DOMContentLoaded", () => {
    addMessage("Diagbot", "Seja Bem-Vindo! Sou o Chatbot e estou aqui para ajudar. Qual é o seu nome?", "bot-message");
});

// Sends a message from the user to the server
async function sendMessage(userInput = null) {
    const inputField = document.getElementById("user-input");

    // Get text from input if not passed as a parameter
    if (!userInput) {
        userInput = inputField.value.trim();
        if (!userInput) return; // Do nothing if empty
    }

    // Show user message in chat
    addMessage("Você", userInput, "user-message");
    inputField.value = "";

    try {
        // Send message to backend
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userInput })
        });

        // Process the response
        const data = await response.json();
        processBotResponse(data);
    } catch (error) {
        // Show error if fetch fails
        console.error("Erro:", error);
        addMessage("DiagBot", "Desculpe, ocorreu um erro. Tente novamente mais tarde.", "error-message");
    }
}

// Handles bot's reply
function processBotResponse(data) {
    if (!data.response) {
        addMessage("DiagBot", "Desculpe, não entendi sua mensagem.", "bot-message");
        return;
    }

    // Show bot message
    addMessage("DiagBot", data.response, "bot-message");

    // Show note if exists
    if (data.note) {
        addMessage("DiagBot", data.note, "note-message");
    }

    // If chat ends, show restart button
    if (data.end_chat) {
        setTimeout(addRestartButton, 2000);
        return;
    }

    // Ask if the user wants more help
    if (data.ask_more) {
        setTimeout(() => {
            addMessage("DiagBot", "Gostaria de mais alguma coisa?", "bot-message");
            addYesNoButtons();
        }, 1000);
    }
}

// Adds a message to chatbox
function addMessage(sender, message, className) {
    const chatbox = document.getElementById("chatbox");
    if (!chatbox) return;

    const messageContainer = document.createElement("div");
    messageContainer.classList.add("message", className);
    messageContainer.innerHTML = `<p><strong>${sender}:</strong> ${message}</p>`;

    chatbox.appendChild(messageContainer);
    chatbox.scrollTop = chatbox.scrollHeight; // Auto-scroll
}

// Adds "Yes" and "No" buttons for more interaction
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

// Ends the chat with a goodbye message
function endChat() {
    addMessage("DiagBot", "Ok! Se precisar de algo no futuro, estarei aqui. Tenha um ótimo dia!", "bot-message");
    setTimeout(addRestartButton, 2000);
}

// Creates "Restart conversation" button
function addRestartButton() {
    removeElementById("button-container");

    const chatbox = document.getElementById("chatbox");
    const restartButtonContainer = document.createElement("div");
    restartButtonContainer.id = "button-container";

    const restartButton = document.createElement("button");
    restartButton.classList.add("restart-btn");
    restartButton.innerText = "Reiniciar conversa";

    // Sends restart command and reloads the page
    restartButton.onclick = async () => {
        await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: 'reiniciar' })
        });
        location.reload();
    };

    restartButtonContainer.appendChild(restartButton);
    chatbox.appendChild(restartButtonContainer);
}

// Removes an element by its ID
function removeElementById(elementId) {
    const element = document.getElementById(elementId);
    if (element) element.remove();
}

// Theme switcher on page load
document.addEventListener("DOMContentLoaded", () => {
    const themeToggleButton = document.getElementById("theme-toggle");
    const body = document.body;

    // Set dark mode if saved in localStorage
    if (localStorage.getItem("theme") === "dark") {
        body.classList.add("dark-mode");
        themeToggleButton.innerText = "☀️ Modo Claro";
    }

    // Toggle dark/light mode
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

// Send message on Enter key press
document.getElementById("user-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
});

// --- Alternate chat form handling ---
const form = document.getElementById('chat-form');
const input = document.getElementById('message-input');
const chatBox = document.getElementById('chat-box');

// Append a new message to chat
function appendMessage(text, sender) {
    const div = document.createElement('div');
    div.classList.add('message', sender);
    div.innerHTML = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Handle chat form submit
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = input.value.trim();
    if (!message) return;

    appendMessage(message, 'user'); // Show user message
    input.value = '';
    input.disabled = true; // Disable input while waiting

    try {
        // Send to backend and get response
        const response = await fetch('{{ url_for("chat_api") }}', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message})
        });
        const data = await response.json();
        appendMessage(data.response, 'bot'); // Show bot reply
    } catch (err) {
        appendMessage('Erro ao se comunicar com o servidor.', 'bot');
    } finally {
        input.disabled = false;
        input.focus(); // Refocus input
    }
});
