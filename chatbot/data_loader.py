import json
import os
import nltk
import shutil
from nltk.tokenize import word_tokenize

nltk.data.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'nltk_data'))

# Ensure punkt_tab/english/english.pickle exists for NLTK compatibility
punkt_dir = os.path.join(os.path.dirname(__file__), '..', 'nltk_data', 'tokenizers', 'punkt')
punkt_tab_english_dir = os.path.join(os.path.dirname(__file__), '..', 'nltk_data', 'tokenizers', 'punkt_tab', 'english')
english_pickle = os.path.join(punkt_dir, 'english.pickle')
english_tab_pickle = os.path.join(punkt_tab_english_dir, 'english.pickle')

os.makedirs(punkt_tab_english_dir, exist_ok=True)
if os.path.exists(english_pickle) and not os.path.exists(english_tab_pickle):
    shutil.copy2(english_pickle, english_tab_pickle)

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