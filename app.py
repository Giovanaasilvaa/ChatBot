import google.generativeai as genai
from flask import Flask, request, jsonify, render_template, session

# Configurar a API do Google Gemini
genai.configure(api_key="sua chave aqui")  

app = Flask(__name__)
app.secret_key = "segredo_seguro"


CONDITIONS = {
    "febre": {
        "Infecções virais": ["Gripe", "COVID-19", "Resfriado comum", "Dengue", "Zika", "Chikungunya"],
        "Infecções bacterianas": ["Pneumonia", "Meningite", "Infecção urinária", "Tuberculose"],
        "Outras condições médicas": ["Lúpus", "Câncer", "Doenças autoimunes"]
    },
    "tosse": {
        "Infecções respiratórias": ["Bronquite", "Pneumonia", "COVID-19", "Tuberculose"],
        "Outras condições": ["Asma", "Refluxo gastroesofágico", "Alergias", "Doença pulmonar obstrutiva crônica (DPOC)"]
    },
    "dor de cabeça": {
        "Neurológicas": ["Enxaqueca", "Cefaleia tensional", "Neuralgia do trigêmeo"],
        "Infecciosas": ["Sinusite", "Meningite", "Encefalite"],
        "Vasculares": ["Acidente vascular cerebral (AVC)", "Hipertensão"]
    },
    "dor abdominal": {
        "Gastrointestinais": ["Gastrite", "Úlcera", "Refluxo", "Síndrome do intestino irritável"],
        "Infecções": ["Apendicite", "Infecção intestinal", "Hepatite"]
    },
    "fadiga": {
        "Causas comuns": ["Estresse", "Falta de sono", "Anemia", "Depressão"],
        "Doenças crônicas": ["Hipotireoidismo", "Diabetes", "Síndrome da fadiga crônica"]
    },
    "náusea": {
        "Gastrointestinais": ["Gastrite", "Refluxo", "Intoxicação alimentar"],
        "Neurológicas": ["Enxaqueca", "Labirintite"]
    }
}

def format_conditions(symptom_details):

    formatted_text = ""
    for category, diseases in symptom_details.items():
        formatted_text += f"<strong>{category}:</strong><br>"
        formatted_text += "<br>".join(f"  - {disease}" for disease in diseases) + "<br><br>"
    return formatted_text

@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip().lower()

    if not user_message:
        return jsonify({"response": "Por favor, digite algo!"})

   
    if "name" not in session:
        session["name"] = user_message
        return jsonify({
            "response": f"Certo, {session['name']}, informe os sintomas separados por vírgula, como 'febre, tosse'."
        })

    
    if user_message == "sim":
        return jsonify({"response": "Por favor, informe os novos sintomas separados por vírgula."})

   
    if user_message == "não":
        return jsonify({
            "response": "Ok! Se precisar de algo no futuro, estarei aqui. Tenha um ótimo dia!",
            "end_chat": True
        })

   
    symptoms = [s.strip() for s in user_message.split(",")]
    response_text = ""

    for symptom in symptoms:
        if symptom in CONDITIONS:
            formatted_conditions = format_conditions(CONDITIONS[symptom])
            response_text += f"<strong>{symptom.capitalize()}:</strong><br>{formatted_conditions}"

    
    if not response_text:
        model = genai.GenerativeModel("gemini-pro")
        gemini_response = model.generate_content(
            f"O usuário relatou os seguintes sintomas: {user_message}. Quais doenças podem estar associadas a esses sintomas? "
            "Liste cada doença em tópicos e categorize-as se possível."
        )
        gemini_text = gemini_response.text.replace("\n", "<br>")

        return jsonify({
            "response": f"Não encontrei esse sintoma na minha base, mas aqui está o que o Google Gemini sugere:<br><br>{gemini_text}",
            "note": "Este diagnóstico é apenas uma orientação. Consulte um médico para um diagnóstico preciso.",
            "ask_more": True
        })

    return jsonify({
        "response": response_text,
        "note": "Este diagnóstico é apenas uma orientação. Consulte um médico para um diagnóstico preciso.",
        "ask_more": True
    })


if __name__ == '__main__':
    app.run(debug=True)
