import torch
import torch.nn as nn
import torch.optim as optim
from model import ChatbotModel
from data_loader import load_intents
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# Load intents
vocabulary, intents, intent_responses = load_intents("intents.json")

# Convert training data using TF-IDF
vectorizer = TfidfVectorizer()
X_train_texts = [" ".join(patterns) for patterns in intent_responses.values()]
X_train = vectorizer.fit_transform(X_train_texts).toarray()  # Ensure fitting happens here
y_train = [intents.index(intent) for intent in intents]

X_train = torch.tensor(X_train, dtype=torch.float32)
y_train = torch.tensor(y_train, dtype=torch.long)

# Define model dimensions
input_size = len(X_train[0])
output_size = len(intents)

# Save dimensions and TF-IDF vocabulary
dimensions = {"input_size": input_size, "output_size": output_size}
with open("dimensions.json", "w") as f:
    json.dump(dimensions, f)

with open("tfidf_vocab.json", "w") as f:
    json.dump(vectorizer.vocabulary_, f)  # Save fitted vocabulary

# Initialize model
model = ChatbotModel(input_size, output_size)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Train model
for epoch in range(1000):
    optimizer.zero_grad()
    output = model(X_train)
    loss = criterion(output, y_train)
    loss.backward()
    optimizer.step()
    if epoch % 100 == 0:
        print(f"Epoch {epoch}, Loss: {loss.item()}")

# Save trained model
torch.save(model.state_dict(), "chatbot_model.pth")
print("Model trained and saved as chatbot_model.pth")