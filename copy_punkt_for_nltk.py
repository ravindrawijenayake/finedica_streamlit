import shutil
import os

# Ensure punkt_tab/english/ exists and has english.pickle
punkt_dir = os.path.join(os.path.dirname(__file__), 'nltk_data', 'tokenizers', 'punkt')
punkt_tab_english_dir = os.path.join(os.path.dirname(__file__), 'nltk_data', 'tokenizers', 'punkt_tab', 'english')
english_pickle = os.path.join(punkt_dir, 'english.pickle')
english_tab_pickle = os.path.join(punkt_tab_english_dir, 'english.pickle')

os.makedirs(punkt_tab_english_dir, exist_ok=True)

if os.path.exists(english_pickle) and not os.path.exists(english_tab_pickle):
    shutil.copy2(english_pickle, english_tab_pickle)
    print(f"Copied {english_pickle} to {english_tab_pickle}")
else:
    print(f"punkt_tab/english/ already has english.pickle or source is missing.")
