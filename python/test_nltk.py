import nltk
from nltk.tokenize import word_tokenize

nltk.data.path.append('C:\\Users\\Administrator\\AppData\\Roaming\\nltk_data')

# Test the tokenizer
text = "Hello, how are you?"
tokens = word_tokenize(text)
print("Tokens:", tokens)