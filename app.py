import google.generativeai as genai
from flask import Flask, request, jsonify, render_template, session
from collections import defaultdict
import sys
import os
from dotenv import load_dotenv
import secrets

load_dotenv()

# Google Gemini API Configuration
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")


app = Flask(
    __name__,
    template_folder=os.path.join(base_path, "templates"), 
    static_folder=os.path.join(base_path, "static")
)

app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(16))

# Knowledge base for symptom combinations
COMBINACOES_SINTOMAS = {

    # Breathing patterns
    ("febre", "tosse", "dor de cabeça"): [
        "COVID-19",
        "Gripe (Influenza)",
        "Sinusite aguda"
    ],
    ("febre", "dor de garganta", "tosse"): [
        "Amigdalite bacteriana",
        "Mononucleose",
        "Faringite viral"
    ],
    
    # Gastrointestinal patterns
    ("náusea", "dor abdominal", "diarreia"): [
        "Gastroenterite viral",
        "Intoxicação alimentar"
    ],
    
    # Neurological patterns
    ("dor de cabeça", "náusea", "tontura"): [
        "Enxaqueca",
        "Labirintite"
    ],
    
    # Medical emergencies
    ("febre alta", "rigidez de nuca", "dor de cabeça"): [
        "Meningite (PROCURE ATENDIMENTO URGENTE)"
    ],
    
    # Common conditions
    ("fadiga", "dor muscular", "dor de cabeça"): [
        "Estresse prolongado",
        "Quadro viral"
    ]
}

# Database of individual conditions
CONDICOES = {
    "febre": {
        "Infecções virais": ["Gripe", "COVID-19", "Dengue"],
        "Infecções bacterianas": ["Amigdalite", "Pneumonia", "Infecção urinária"],
        "Outras": ["Sinusite"]
    },
    "tosse": {
        "Comuns": ["Resfriado", "Bronquite", "Asma", "Alergia"],
        "Preocupantes": ["Pneumonia", "COVID-19"]
    },
    "dor de cabeça": {
        "Comuns": ["Enxaqueca", "Cefaleia tensional", "Sinusite"],
        "Preocupantes": ["Meningite"]
    },
    "dor abdominal": {
        "Comuns": ["Gastrite", "Intoxicação alimentar"],
        "Emergências": ["Apendicite"]
    },
    "fadiga": {
        "Causas": ["Anemia", "Estresse", "Hipotireoidismo"]
    },
    "náusea": {
        "Comuns": ["Gastrite", "Labirintite"]
    }
}

def encontrar_combinacoes(sintomas):
    """Finds diseases that match ALL reported symptoms"""
    sintomas_set = set(s.strip().lower() for s in sintomas)
    combinacoes_encontradas = []
    
    # First check known combinations
    for combinacao, doencas in COMBINACOES_SINTOMAS.items():
        if set(combinacao).issubset(sintomas_set):
            combinacoes_encontradas.extend(doencas)
    
    return combinacoes_encontradas

def encontrar_doencas_comuns(sintomas):
    """Find common diseases by individual symptoms"""
    contagem_doencas = defaultdict(int)
    conjuntos_doencas = []
    
    for sintoma in sintomas:
        if sintoma in CONDICOES:
            doencas = set()
            for categoria in CONDICOES[sintoma].values():
                doencas.update(categoria)
            conjuntos_doencas.append(doencas)
            
            for doenca in doencas:
                contagem_doencas[doenca] += 1
    
    if not conjuntos_doencas:
        return set()
    
    # Returns only diseases that appear in ALL sets
    doencas_comuns = set.intersection(*conjuntos_doencas)
    return doencas_comuns

def formatar_lista_doencas(doencas):
    """Formats the disease list with priority indicators"""
    doencas_prioritarias = {
        "COVID-19": "🦠",
        "Pneumonia": "⚠️",
        "Meningite": "🚨",
        "Apendicite": "🚨"
    }
    
    formatado = []
    for doenca in sorted(doencas):
        emoji = doencas_prioritarias.get(doenca, "")
        formatado.append(f"{emoji} {doenca}" if emoji else f"- {doenca}")
    return "<br>".join(formatado)

@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

@app.route('/chat', methods=['GET'])
def chat_page():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    mensagem = data.get("message", "").strip().lower()
    
    if mensagem == "reiniciar":
        session.clear()
        return jsonify({"response": "Conversa reiniciada! Qual é o seu nome?"})

    if not mensagem:
        return jsonify({"response": "Por favor, digite algo!"})

    if "nome" not in session:
        session["nome"] = mensagem
        return jsonify({
            "response": f"Certo, {session['nome']}, informe seus sintomas separados por vírgula (ex: 'febre, tosse'):"
        })

    # Answers to "yes" or "no"
    if mensagem == "sim":
        return jsonify({"response": "Por favor, informe os novos sintomas:"})
    if mensagem == "não":
        session.clear()
        return jsonify({
            "response": "Ok! Melhoras! 😊",
            "end_chat": True
        })

   # Symptom processing
    sintomas = [s.strip() for s in mensagem.split(",")]
    
   #1. First try to find known combinations
    combinacoes = encontrar_combinacoes(sintomas)
    
    if combinacoes:
        resposta = "<strong>Possíveis diagnósticos para esta combinação:</strong><br><br>"
        resposta += formatar_lista_doencas(combinacoes)
        
        # Adiciona recomendações específicas
        if "COVID-19" in combinacoes:
            resposta += "<br><br>💡 Considere fazer um teste para COVID-19"
        if "Meningite" in resposta:
            resposta += "<br><br>🚨 <strong>PROCURE ATENDIMENTO MÉDICO IMEDIATAMENTE</strong>"
    
    else:
        #2. If you don't find any matches, look for common diseases.
        doencas_comuns = encontrar_doencas_comuns(sintomas)
        
        if doencas_comuns:
            resposta = "<strong>Possíveis causas para seus sintomas:</strong><br><br>"
            resposta += formatar_lista_doencas(doencas_comuns)
        else:
            #3. Fallback to Gemini if you don't recognize the symptoms
            try:
                modelo = genai.GenerativeModel("gemini-pro")
                prompt = f"Quais as 3 principais doenças que podem causar estes sintomas juntos: {mensagem}? Responda de forma concisa."
                resposta_gemini = modelo.generate_content(prompt)
                resposta = f"<strong>Análise do Gemini:</strong><br>{resposta_gemini.text.replace('\n', '<br>')}"
            except Exception:
                resposta = "Não reconheci esses sintomas. Por favor, descreva melhor ou consulte um médico."

    return jsonify({
        "response": resposta,
        "note": "⚠️ Este é apenas um guia. Consulte um médico para diagnóstico preciso.",
        "ask_more": True
    })

if __name__ == '__main__':
    app.run(debug=True)
