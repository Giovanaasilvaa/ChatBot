import google.generativeai as genai
from flask import Flask, request, jsonify, render_template, session
from collections import defaultdict
import sys
import os
from dotenv import load_dotenv
import secrets

load_dotenv()  # Load environment variables from .env file

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # Configure Gemini AI API key

# Define base path for app resources depending on packaging
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

# Initialize Flask app with custom template and static folders
app = Flask(
    __name__,
    template_folder=os.path.join(base_path, "templates"), 
    static_folder=os.path.join(base_path, "static")
)

# Set secret key for session management
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(16))

# Symptom combinations mapped to possible diagnoses
COMBINACOES_SINTOMAS = {
    ("febre", "tosse", "dor de cabeça"): [
        "COVID-19",
        "Gripe (Influenza)",
        "Sinusite aguda",
        "Pneumonia"
    ],
    ("febre", "tosse", "dor abdominal"): [
        "Pneumonia atípica",
        "COVID-19 (casos gastrointestinais)",
        "Infecção intestinal com complicação respiratória"
    ],
    ("febre", "dor de garganta", "tosse"): [
        "Amigdalite bacteriana",
        "Mononucleose",
        "Faringite viral"
    ],
    ("náusea", "dor abdominal", "diarreia"): [
        "Gastroenterite viral",
        "Intoxicação alimentar",
        "Apendicite inicial"
    ],
    ("febre", "dor abdominal", "náusea"): [
        "Infecção intestinal",
        "Apendicite",
        "Diverticulite"
    ],
    ("dor de cabeça", "náusea", "tontura"): [
        "Enxaqueca",
        "Labirintite"
    ],
    ("febre alta", "rigidez de nuca", "dor de cabeça"): [
        "Meningite (PROCURE ATENDIMENTO URGENTE)"
    ],
    ("dor abdominal intensa", "febre", "náusea"): [
        "Apendicite aguda (PROCURE ATENDIMENTO URGENTE)",
        "Peritonite"
    ],
    ("fadiga", "dor muscular", "dor de cabeça"): [
        "Estresse prolongado",
        "Quadro viral"
    ]
}

# Individual symptoms mapped to common diseases by category
CONDICOES = {
    "febre": {
        "Infecções": ["Gripe", "COVID-19", "Dengue", "Infecção bacteriana"],
        "Outras": ["Sinusite", "Reação medicamentosa"]
    },
    "tosse": {
        "Respiratórias": ["Resfriado", "Bronquite", "Asma", "Pneumonia"],
        "Alérgicas": ["Rinite alérgica"]
    },
    "dor de cabeça": {
        "Primárias": ["Enxaqueca", "Cefaleia tensional"],
        "Secundárias": ["Sinusite", "Desidratação"]
    },
    "dor abdominal": {
        "Digestivas": ["Gastrite", "Intoxicação alimentar", "Síndrome do intestino irritável"],
        "Emergências": ["Apendicite", "Pedra na vesícula"]
    },
    "náusea": {
        "Gastrointestinais": ["Gastrite", "Labirintite", "Gravidez"]
    }
}

def encontrar_combinacoes(sintomas):
    """Find matching symptom combinations and return possible diagnoses"""
    sintomas_normalizados = [s.strip().lower() for s in sintomas]
    combinacoes = []
    
    # Check exact matches for all symptoms in combos
    for combo, diagnosticos in COMBINACOES_SINTOMAS.items():
        if all(sintoma in sintomas_normalizados for sintoma in combo):
            combinacoes.extend(diagnosticos)
    
    # If no exact, check partial matches with at least 2 symptoms
    if not combinacoes:
        for combo, diagnosticos in COMBINACOES_SINTOMAS.items():
            if sum(1 for sintoma in combo if sintoma in sintomas_normalizados) >= 2:
                combinacoes.extend(diagnosticos)
    
    return list(set(combinacoes))  # Remove duplicates

def encontrar_doencas_comuns(sintomas):
    """Find diseases common to all given symptoms"""
    sintomas_normalizados = [s.strip().lower() for s in sintomas]
    conjuntos = []
    
    # Gather diseases linked to each symptom
    for sintoma in sintomas_normalizados:
        if sintoma in CONDICOES:
            doencas = set()
            for categoria in CONDICOES[sintoma].values():
                doencas.update(categoria)
            conjuntos.append(doencas)
    
    # Return intersection (common diseases) or empty set
    return set.intersection(*conjuntos) if conjuntos else set()

def formatar_resposta(doencas):
    """Format disease list with priority icons"""
    prioridades = {
        "COVID-19": "🦠",
        "Pneumonia": "⚠️", 
        "Meningite": "🚨",
        "Apendicite": "🚨"
    }
    
    formatado = []
    for doenca in sorted(doencas):
        prefixo = prioridades.get(doenca, "•")
        formatado.append(f"{prefixo} {doenca}")
    
    return "<br>".join(formatado)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    mensagem = data.get("message", "").strip().lower()
    
    # Reset conversation if requested
    if mensagem == "reiniciar":
        session.clear()
        return jsonify({"response": "Conversa reiniciada! Qual é o seu nome?"})

    # Validate empty input
    if not mensagem:
        return jsonify({"response": "Por favor, digite algo!"})

    # Set user name if not set yet
    if "nome" not in session:
        session["nome"] = mensagem
        return jsonify({
            "response": f"Olá {session['nome']}, quais sintomas você está sentindo? (ex: febre, dor de cabeça)",
            "ask_more": False  # Do not ask again yet
        })

    # Handle yes/no answers for continuing conversation
    if mensagem in ["sim", "não"]:
        if mensagem == "sim":
            return jsonify({
                "response": "Por favor, descreva seus sintomas.",
                "ask_more": False  # Await symptoms input
            })
        else:
            session.clear()
            return jsonify({
                "response": "Tudo bem! Se precisar, volte sempre. Até mais!",
                "ask_more": False  # End conversation
            })

    sintomas = [s.strip() for s in mensagem.split(",")]

    combinacoes = encontrar_combinacoes(sintomas)
    
    # Prepare diagnostic response based on symptom combos
    if combinacoes:
        resposta = "<strong>Possíveis diagnósticos:</strong><br><br>"
        resposta += formatar_resposta(combinacoes)
        
        # Add warnings for serious conditions
        if any(d in combinacoes for d in ["COVID-19", "Pneumonia"]):
            resposta += "<br><br>💡 Considere procurar atendimento médico"
        if any(d in combinacoes for d in ["Meningite", "Apendicite aguda"]):
            resposta += "<br><br>🚨 <strong>PROCURE ATENDIMENTO URGENTE</strong>"
    else:
        # Try to find common diseases if no combos found
        doencas_comuns = encontrar_doencas_comuns(sintomas)
        
        if doencas_comuns:
            resposta = "<strong>Possíveis causas:</strong><br><br>"
            resposta += formatar_resposta(doencas_comuns)
        else:
            # Fallback to AI model for suggestions
            try:
                modelo = genai.GenerativeModel("gemini-pro")
                prompt = f"Liste as 3 principais possibilidades médicas para estes sintomas juntos: {mensagem}. Seja conciso."
                resposta_ai = modelo.generate_content(prompt)
                resposta = f"<strong>Sugestões:</strong><br>{resposta_ai.text.replace('\n', '<br>')}"
            except Exception:
                resposta = "Não encontrei correspondência exata. Descreva melhor ou consulte um médico."

    # Return response with note and ask if user wants to continue
    return jsonify({
        "response": resposta,
        "note": "⚠️ Esta é apenas uma orientação inicial. Consulte um médico para diagnóstico preciso.",
        "ask_more": True
    })

@app.route('/')
def index():
    session.clear()  # Clear session on main page load
    return render_template('index.html')

@app.route('/chat', methods=['GET'])
def chat_page():
    return render_template('chat.html')

if __name__ == '__main__':
    app.run(debug=True)
