# finedica_streamlit/app.py
# Main entry point for the Streamlit version of FINEDICA
import streamlit as st
from pathlib import Path
import sqlite3
import hashlib
import torch
import random
import json
from nltk.tokenize import word_tokenize
import os
import nltk

nltk.data.path.append(os.path.join(os.path.dirname(__file__), 'nltk_data'))
nltk.download('punkt', quiet=True, force=True)

st.set_page_config(page_title="FINEDICA Streamlit App", layout="wide")

# --- User Authentication Helpers ---
DB_PATH = Path("user_auth.db")

def create_user_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        first_name TEXT,
        last_name TEXT,
        gender TEXT
    )''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email, password, first_name, last_name, gender):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO users (email, password, first_name, last_name, gender) VALUES (?, ?, ?, ?, ?)',
                  (email, hash_password(password), first_name, last_name, gender))
        conn.commit()
        conn.close()
        return True, "Registration successful."
    except sqlite3.IntegrityError:
        return False, "Email already registered."
    except Exception as e:
        return False, str(e)

def login_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email=? AND password=?', (email, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

# --- Psychometric Test ---
PSYCH_DB_PATH = Path("psychometric_responses.db")

def create_psychometric_table():
    conn = sqlite3.connect(PSYCH_DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS psychometricresponse (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        q1 INTEGER, q2 INTEGER, q3 INTEGER, q4 INTEGER, q5 INTEGER,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def save_psychometric_response(email, answers):
    conn = sqlite3.connect(PSYCH_DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO psychometricresponse (email, q1, q2, q3, q4, q5) VALUES (?, ?, ?, ?, ?, ?)',
              (email, *answers))
    conn.commit()
    conn.close()

def get_latest_psychometric(email):
    conn = sqlite3.connect(PSYCH_DB_PATH)
    c = conn.cursor()
    c.execute('SELECT q1, q2, q3, q4, q5, submitted_at FROM psychometricresponse WHERE email=? ORDER BY id DESC LIMIT 1', (email,))
    row = c.fetchone()
    conn.close()
    return row

# --- Future Self ---
FUTURE_DB_PATH = Path("future_self_responses.db")

def create_future_self_table():
    conn = sqlite3.connect(FUTURE_DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS future_self (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        q1 TEXT, q2 TEXT, q3 TEXT, q4 TEXT, q5 TEXT,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def save_future_self_response(email, answers):
    conn = sqlite3.connect(FUTURE_DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO future_self (email, q1, q2, q3, q4, q5) VALUES (?, ?, ?, ?, ?, ?)',
              (email, *answers))
    conn.commit()
    conn.close()

def get_latest_future_self(email):
    conn = sqlite3.connect(FUTURE_DB_PATH)
    c = conn.cursor()
    c.execute('SELECT q1, q2, q3, q4, q5, submitted_at FROM future_self WHERE email=? ORDER BY id DESC LIMIT 1', (email,))
    row = c.fetchone()
    conn.close()
    return row

# --- Expenditure Tracker ---
EXP_DB_PATH = Path("expenditure_records.db")

def create_expenditure_table():
    conn = sqlite3.connect(EXP_DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenditure (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        category TEXT,
        amount REAL,
        note TEXT,
        spent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def save_expenditure(email, category, amount, note):
    conn = sqlite3.connect(EXP_DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO expenditure (email, category, amount, note) VALUES (?, ?, ?, ?)',
              (email, category, amount, note))
    conn.commit()
    conn.close()

def get_expenditures(email):
    conn = sqlite3.connect(EXP_DB_PATH)
    c = conn.cursor()
    c.execute('SELECT category, amount, note, spent_at FROM expenditure WHERE email=? ORDER BY spent_at DESC LIMIT 20', (email,))
    rows = c.fetchall()
    conn.close()
    return rows

# --- Face Upload & Avatar Generation ---
AVATAR_DIR = Path("avatars")
AVATAR_DIR.mkdir(exist_ok=True)

def get_avatar_path(email):
    safe_email = email.replace('@', '_at_').replace('.', '_dot_')
    return AVATAR_DIR / f"avatar_{safe_email}.png"

def save_uploaded_face(email, uploaded_file):
    avatar_path = get_avatar_path(email)
    with open(avatar_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return avatar_path

def avatar_exists(email):
    return get_avatar_path(email).exists()

# --- Chatbot Model Loading (local, simple version) ---
CHATBOT_DIR = Path("chatbot")
with open(CHATBOT_DIR / "intents.json", "r") as f:
    chatbot_intents = json.load(f)

with open(CHATBOT_DIR / "dimensions.json", "r") as f:
    dimensions = json.load(f)

from chatbot.model import ChatbotModel
from chatbot.data_loader import load_intents
vocabulary, intents, intent_responses = load_intents(str(CHATBOT_DIR / "intents.json"))

model = ChatbotModel(dimensions['input_size'], dimensions['output_size'])
model.load_state_dict(torch.load(str(CHATBOT_DIR / "chatbot_model.pth"), map_location=torch.device('cpu')))
model.eval()

def bag_of_words(sentence):
    sentence_words = word_tokenize(sentence)
    bag = [1 if word in sentence_words else 0 for word in vocabulary]
    return torch.tensor([bag], dtype=torch.float32)

def get_chatbot_response(message):
    bag = bag_of_words(message)
    with torch.no_grad():
        output = model(bag)
    _, predicted = torch.max(output, dim=1)
    tag = intents[predicted.item()]
    response = random.choice(intent_responses[tag])
    return response

create_user_table()
create_psychometric_table()
create_future_self_table()
create_expenditure_table()

# --- Streamlit UI ---

if 'user' not in st.session_state:
    st.session_state['user'] = None

# Authentication page
if st.session_state['user'] is None:
    st.sidebar.header("Login or Register")
    auth_mode = st.sidebar.radio("Select", ["Login", "Register"])
    if auth_mode == "Register":
        st.title("User Registration")
        with st.form("register_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            gender = st.selectbox("Gender", ["", "Male", "Female", "Other"])
            submitted = st.form_submit_button("Register")
            if submitted:
                ok, msg = register_user(email, password, first_name, last_name, gender)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
    else:
        st.title("User Login")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                user = login_user(email, password)
                if user:
                    st.session_state['user'] = {
                        'id': user[0],
                        'email': user[1],
                        'first_name': user[3],
                        'last_name': user[4],
                        'gender': user[5]
                    }
                    st.success("Login successful!")
                    st.experimental_rerun()
                else:
                    st.error("Invalid email or password.")
    st.stop()

# Sidebar navigation
st.sidebar.title("FINEDICA Navigation")
page = st.sidebar.radio("Go to", [
    "Home",
    "Chatbot",
    "Avatar Generation",
    "Expenditure Tracker",
    "Psychometric Test",
    "Future Self"
])

# Home page
if page == "Home":
    st.title("Welcome to FINEDICA (Streamlit Edition)")
    st.markdown("""
    This is a Streamlit-based version of the FINEDICA platform. Use the sidebar to navigate between features:
    - Chatbot: Ask financial questions and get AI-powered answers.
    - Avatar Generation: Create or view your financial avatar.
    - Expenditure Tracker: Track and analyze your spending.
    - Psychometric Test: Take the test and view your results.
    - Future Self: Visualize and plan your financial future.
    """)

# Placeholder for other pages (to be implemented)
elif page == "Chatbot":
    st.header("Chatbot")
    user_email = st.session_state['user']['email']
    st.write(f"Logged in as: {user_email}")
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    st.subheader("Ask a financial question:")
    with st.form("chatbot_form"):
        user_message = st.text_input("You:")
        submitted = st.form_submit_button("Send")
        if submitted and user_message.strip():
            response = get_chatbot_response(user_message)
            st.session_state['chat_history'].append((user_message, response))
    for user_msg, bot_resp in st.session_state['chat_history']:
        st.markdown(f"**You:** {user_msg}")
        st.markdown(f"**Bot:** {bot_resp}")
elif page == "Avatar Generation":
    st.header("Avatar Generation & Face Upload")
    user_email = st.session_state['user']['email']
    st.write(f"Logged in as: {user_email}")
    avatar_path = get_avatar_path(user_email)
    if avatar_exists(user_email):
        st.image(str(avatar_path), caption="Your Avatar", width=200)
        if st.button("Remove Avatar"):
            avatar_path.unlink(missing_ok=True)
            st.success("Avatar removed.")
            st.rerun()
    st.subheader("Upload a Face Image to Generate Avatar")
    uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        save_uploaded_face(user_email, uploaded_file)
        st.success("Face image uploaded! Avatar updated.")
        st.experimental_rerun()
    st.info("Avatar generation is simulated by saving the uploaded image as your avatar. For real avatar generation, integrate with your ML model here.")
elif page == "Expenditure Tracker":
    st.header("Expenditure Tracker")
    user_email = st.session_state['user']['email']
    st.write(f"Logged in as: {user_email}")
    st.subheader("Add New Expenditure")
    with st.form("expenditure_form"):
        category = st.selectbox("Category", ["Food", "Transport", "Bills", "Shopping", "Other"])
        amount = st.number_input("Amount", min_value=0.0, step=0.01)
        note = st.text_input("Note (optional)")
        submitted = st.form_submit_button("Add Expenditure")
        if submitted:
            save_expenditure(user_email, category, amount, note)
            st.success("Expenditure added!")
            st.experimental_rerun()
    st.subheader("Recent Expenditures")
    records = get_expenditures(user_email)
    if records:
        st.table([{"Category": r[0], "Amount": r[1], "Note": r[2], "Date": r[3]} for r in records])
    else:
        st.info("No expenditures recorded yet.")
elif page == "Psychometric Test":
    st.header("Psychometric Test")
    user_email = st.session_state['user']['email']
    st.write(f"Logged in as: {user_email}")
    latest = get_latest_psychometric(user_email)
    if latest:
        st.subheader("Your Last Psychometric Test Result:")
        st.write({f"Q{i+1}": v for i, v in enumerate(latest[:5])})
        st.write(f"Submitted at: {latest[5]}")
        if st.button("Retake Test"):
            st.session_state['show_psych_form'] = True
    if 'show_psych_form' not in st.session_state:
        st.session_state['show_psych_form'] = not bool(latest)
    if st.session_state['show_psych_form']:
        st.subheader("Take the Psychometric Test")
        with st.form("psychometric_form"):
            q1 = st.slider("I enjoy planning my finances.", 1, 5, 3)
            q2 = st.slider("I feel confident about my financial future.", 1, 5, 3)
            q3 = st.slider("I often save money from my income.", 1, 5, 3)
            q4 = st.slider("I am comfortable taking financial risks.", 1, 5, 3)
            q5 = st.slider("I seek advice before making big purchases.", 1, 5, 3)
            submitted = st.form_submit_button("Submit Test")
            if submitted:
                save_psychometric_response(user_email, [q1, q2, q3, q4, q5])
                st.success("Test submitted!")
                st.session_state['show_psych_form'] = False
                st.experimental_rerun()
elif page == "Future Self":
    st.header("Future Self Questionnaire")
    user_email = st.session_state['user']['email']
    st.write(f"Logged in as: {user_email}")
    latest = get_latest_future_self(user_email)
    if latest:
        st.subheader("Your Last Future Self Submission:")
        for i, v in enumerate(latest[:5]):
            st.write(f"Q{i+1}: {v}")
        st.write(f"Submitted at: {latest[5]}")
        if st.button("Retake Questionnaire"):
            st.session_state['show_future_form'] = True
    if 'show_future_form' not in st.session_state:
        st.session_state['show_future_form'] = not bool(latest)
    if st.session_state['show_future_form']:
        st.subheader("Answer the Future Self Questions")
        with st.form("future_self_form"):
            q1 = st.text_input("Where do you see yourself financially in 5 years?")
            q2 = st.text_input("What is your biggest financial goal?")
            q3 = st.text_input("What financial habits do you want to improve?")
            q4 = st.text_input("What worries you most about your financial future?")
            q5 = st.text_input("What would financial success look like for you?")
            submitted = st.form_submit_button("Submit Questionnaire")
            if submitted:
                save_future_self_response(user_email, [q1, q2, q3, q4, q5])
                st.success("Submission saved!")
                st.session_state['show_future_form'] = False
                st.experimental_rerun()
