from flask import Flask, request, jsonify
import os
import json
import random
import torch
import nltk
import numpy as np
from torch.utils.data import DataLoader, TensorDataset
import torch.nn as nn
import torch.optim as optim

nltk.download('punkt')
nltk.data.path.append('C:\\Users\\Administrator\\AppData\\Roaming\\nltk_data')

# Define the chatbot model
class ChatbotModel(nn.Module):
    def __init__(self, input_size, output_size):
        super(ChatbotModel, self).__init__()
        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, output_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return x

# Define the chatbot assistant
class ChatbotAssistant:
    def __init__(self, intents_path, model_path, dimensions_path):
        self.intents_path = intents_path
        self.model_path = model_path
        self.dimensions_path = dimensions_path
        self.model = None
        self.intents = []
        self.intents_responses = {}
        self.vocabulary = []

        self.load_intents()
        self.load_model()

    def load_intents(self):
        with open(self.intents_path, 'r') as f:
            intents_data = json.load(f)
        for intent in intents_data['intents']:
            self.intents.append(intent['tag'])
            self.intents_responses[intent['tag']] = intent['responses']
            for pattern in intent['patterns']:
                words = nltk.word_tokenize(pattern)
                self.vocabulary.extend(words)
        self.vocabulary = sorted(set(self.vocabulary))

    def load_model(self):
        with open(self.dimensions_path, 'r') as f:
            dimensions = json.load(f)
        self.model = ChatbotModel(dimensions['input_size'], dimensions['output_size'])
        self.model.load_state_dict(torch.load(self.model_path))
        self.model.eval()

    def bag_of_words(self, sentence):
        sentence_words = nltk.word_tokenize(sentence)
        bag = [1 if word in sentence_words else 0 for word in self.vocabulary]
        return torch.tensor([bag], dtype=torch.float32)

    def get_response(self, message):
        bag = self.bag_of_words(message)
        with torch.no_grad():
            output = self.model(bag)
        _, predicted = torch.max(output, dim=1)
        tag = self.intents[predicted.item()]
        return random.choice(self.intents_responses[tag])

# Flask app
app = Flask(__name__)

# Initialize the chatbot assistant
assistant = ChatbotAssistant(
    intents_path='intents.json',
    model_path='chatbot_model.pth',
    dimensions_path='dimensions.json'
)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    response = assistant.get_response(user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)