## 📊 Chat Médico com Flask e API Gemini 

Este é um **chat interativo sobre sintomas de saúde**, desenvolvido como parte de um **trabalho para a faculdade**. A aplicação foi criada com **Python e Flask**, integrando a **API Gemini (Google Generative AI)** para fornecer sugestões inteligentes baseadas nos sintomas descritos pelo usuário.

## 🧠 Funcionalidades

1. **Identificação do Usuário**: O chat solicita o nome do usuário para iniciar a conversa.
2. **Reconhecimento de Sintomas Pré-cadastrados**: A aplicação responde com possíveis doenças relacionadas aos sintomas informados, com base em um banco interno.
3. **Integração com a API Gemini**: Quando o sintoma não está no banco de dados, o sistema consulta a API do Gemini para gerar uma resposta personalizada.
4. **Interação em Tempo Real**: O usuário pode continuar relatando sintomas ou encerrar a conversa.
5. **Interface Simples e Intuitiva**: Página web limpa e funcional para facilitar a usabilidade.

## 🧑‍💻 Tecnologias Utilizadas

1. **Python + Flask**: Responsáveis pela lógica do backend, controle de rotas e integração com a API.
2. **HTML + CSS + JavaScript**: Estruturação e interação da interface com o usuário.
3. **Google Generative AI (Gemini)**: Inteligência artificial generativa que sugere doenças com base nos sintomas digitados.

## ⚙️ Como Usar

1. **Instale as dependências**:
   python -m pip install -r requirements.txt


2. **Adicione sua chave da API Gemini no arquivo `app.py`**:
   genai.configure(api_key="SUA_CHAVE_AQUI")


3. **Execute a aplicação**:
   python app.py
 

4. **Interaja com o chat**:
   - Acesse `http://127.0.0.1:5000` no navegador.
   - Informe seu nome.
   - Digite os sintomas (ex: febre, dor de cabeça).
   - Receba sugestões da base de dados ou da IA (Gemini).
   - Continue a conversa ou digite “não” para encerrar.

## ⚠️ Observações

- O projeto foi feito para fins **educacionais** e não substitui um diagnóstico médico profissional.
- As respostas são geradas com base em informações gerais e inteligência artificial, sem análise clínica real.


