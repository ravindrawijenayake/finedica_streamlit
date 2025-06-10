from flask import Flask, request, jsonify
import torch
import random
import nltk
from nltk.tokenize import word_tokenize
from model import ChatbotModel
from data_loader import load_intents
import json
from flask_cors import CORS
from nltk.corpus import stopwords
import string
from sklearn.feature_extraction.text import TfidfVectorizer
import requests
from pathlib import Path

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load intents and model dimensions
vocabulary, intents, intent_responses = load_intents("intents.json")

with open("dimensions.json", "r") as f:
    dimensions = json.load(f)

with open("tfidf_vocab.json", "r") as f:
    tfidf_vocab = json.load(f)

# Load model
model = ChatbotModel(dimensions['input_size'], dimensions['output_size'])
model.load_state_dict(torch.load("chatbot_model.pth"))
model.eval()

# Load and fit TF-IDF vectorizer
vectorizer = TfidfVectorizer(vocabulary=tfidf_vocab)
vectorizer.fit([" ".join(patterns) for patterns in intent_responses.values()])  # Ensure fitting happens here

STABILITY_API_KEY = 'sk-hV3rJIrVaxzsLiq0FwEQ9RNCYBwvm1NcMXwkYhfpUuABSnds'  # Replace with your actual key
STABILITY_URL = 'https://api.stability.ai/v2beta/stable-image/generate/core'

def generate_stability_image(prompt, user_gender=None):
    # Optionally prepend gender to prompt
    if user_gender:
        prompt = f"{user_gender}. {prompt}"
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    multipart_data = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="prompt"\r\n\r\n{prompt}\r\n'
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="output_format"\r\n\r\npng\r\n'
        f'--{boundary}--\r\n'
    )
    headers = {
        'Authorization': f'Bearer {STABILITY_API_KEY}',
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Accept': 'image/png'
    }
    response = requests.post(STABILITY_URL, data=multipart_data, headers=headers)
    if response.status_code == 200:
        # Save image to a file and return the path (or return the image bytes)
        filename = f"generated_chatbot_avatar.png"
        with open(filename, 'wb') as f:
            f.write(response.content)
        return filename
    else:
        return None

def preprocess_text(sentence):
    """
    Preprocess the input sentence by tokenizing, removing punctuation, and stopwords.
    """
    sentence = sentence.lower()
    tokens = nltk.word_tokenize(sentence)
    tokens = [word for word in tokens if word not in string.punctuation and word not in stop_words]
    return " ".join(tokens)

import requests

def call_ollama(prompt, model='phi3'):
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={'model': model, 'prompt': prompt, 'stream': False, 'options': {'num_predict': 64}}
    )
    if response.ok:
        return response.json().get('response', '').strip()
    return "Sorry, I couldn't get a response from the LLM."

# === RAG (Retrieval-Augmented Generation) Setup ===
try:
    from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
    from llama_index.core.retrievers import VectorIndexRetriever
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.core.settings import Settings
    Settings.llm = None  # Disable LLM in llama_index to avoid OpenAI API key errors
    # Use a small, local embedding model (e.g., BAAI/bge-small-en-v1.5)
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    documents = SimpleDirectoryReader('../data', recursive=True).load_data()
    print(f"Loaded {len(documents)} documents for RAG.")
    for doc in documents:
        print(f"Document metadata: {getattr(doc, 'metadata', {})}")
        print(f"Document preview: {getattr(doc, 'text', '')[:400]}")
    index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
    retriever = VectorIndexRetriever(index=index, similarity_top_k=5)
    rag_enabled = True
except Exception as e:
    import traceback
    print(f"RAG setup failed: {e}\n{traceback.format_exc()}")
    rag_enabled = False

# Flask API for chatbot
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip().lower()
        user_gender = data.get('gender', '').strip().capitalize() if data.get('gender') else None
        user_email = data.get('email', '').strip().lower() if data.get('email') else None

        # Fetch user data for personalization
        user_profile = {}
        psychometric_results = {}
        futureself_results = {}
        expenditure_data = {}
        if user_email:
            try:
                import mysql.connector
                # Connect to MySQL for user profile, futureself, expenditure
                conn = mysql.connector.connect(
                    host='localhost', user='root', password='finedica', database='user_reg_db', auth_plugin='mysql_native_password'
                )
                cursor = conn.cursor(dictionary=True)
                # User profile
                cursor.execute('SELECT first_name, last_name, gender FROM users WHERE email=%s LIMIT 1', (user_email,))
                user_profile = cursor.fetchone() or {}
                # Expenditure (latest)
                cursor.execute('SELECT * FROM expenditure WHERE email=%s ORDER BY id DESC LIMIT 1', (user_email,))
                expenditure_data = cursor.fetchone() or {}
                # Future self (latest)
                cursor.execute('SELECT * FROM future_self_responses WHERE email=%s ORDER BY id DESC LIMIT 1', (user_email,))
                futureself_results = cursor.fetchone() or {}
                cursor.close()
                conn.close()
            except Exception as e:
                print(f"MySQL fetch error: {e}")
            try:
                # Psychometric test (SQLite)
                import sqlite3
                conn = sqlite3.connect('../psychometric_test/responses.db')
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM psychometricresponse WHERE email=? ORDER BY id DESC LIMIT 1', (user_email,))
                row = cursor.fetchone()
                if row:
                    psychometric_results = dict(row)
                cursor.close()
                conn.close()
            except Exception as e:
                print(f"SQLite fetch error: {e}")

        # Build personalization context
        personalization = f"User profile: {user_profile}\nPsychometric test: {psychometric_results}\nFuture self: {futureself_results}\nExpenditure: {expenditure_data}"

        # === RAG: Always answer using your own documents ===
        rag_answer = None
        if rag_enabled:
            try:
                from llama_index.core.retrievers import VectorIndexRetriever
                retriever = VectorIndexRetriever(index=index, similarity_top_k=3)
                nodes = retriever.retrieve(user_message)
                print("RAG retrieved nodes:", nodes)
                if nodes:
                    context = "\n\n".join([node.get_content().strip() for node in nodes[:2]])
                    prompt = f"Context: {context}\n\n{personalization}\n\nUser question: {user_message}\n\nAnswer in a complete, detailed, and personalized manner as a financial coach."
                    llm_response = call_ollama(prompt, model='phi3')
                    print("Ollama LLM response (with RAG context):", llm_response)
                    if llm_response and len(llm_response.split()) > 10:
                        return jsonify({'response': llm_response})
                # If no relevant nodes, set rag_answer to None
            except Exception as rag_e:
                print(f"RAG error: {rag_e}")
                # rag_answer remains None

        # === INTENT-BASED FALLBACK ===
        # Preprocess user message
        processed = preprocess_text(user_message)
        X = vectorizer.transform([processed]).toarray()
        with torch.no_grad():
            output = model(torch.tensor(X, dtype=torch.float32))
            predicted = torch.argmax(output, dim=1).item()
            tag = intents[predicted]
            responses = intent_responses.get(tag, ["I'm not sure how to help with that."])
            import random
            response = random.choice(responses)
        return jsonify({'response': response})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'response': f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)