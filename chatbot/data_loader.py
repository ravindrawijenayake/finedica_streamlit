import json
import nltk
from nltk.tokenize import word_tokenize

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def load_intents(file_path):
    with open(file_path, 'r') as f:
        intents_data = json.load(f)

    vocabulary = []
    intents = []
    intent_responses = {}

    for intent in intents_data['intents']:
        intents.append(intent['tag'])
        intent_responses[intent['tag']] = intent['responses']
        for pattern in intent['patterns']:
            words = word_tokenize(pattern, language="english")
            vocabulary.extend(words)

    return sorted(set(vocabulary)), intents, intent_responses