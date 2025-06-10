# finedica_streamlit
=======
# FINEDICA Streamlit Edition

This folder contains a fully functional Streamlit-based version of the FINEDICA application, ported from the original PHP/JS web app. It is designed for easy deployment on Streamlit Cloud or any Python environment.

## Features
- **User Registration & Login:** Secure authentication using SQLite.
- **Psychometric Test:** Take and review your financial psychometric results.
- **Future Self Questionnaire:** Reflect on your financial goals and plans.
- **Expenditure Tracker:** Add, view, and analyze your spending.
- **Face Upload & Avatar Generation:** Upload a face image to set your avatar (ML integration placeholder).
- **Chatbot:** Ask financial questions and get AI-powered answers using a local model.

## Folder Structure

- `app.py` — Main Streamlit app entry point
- `requirements.txt` — Python dependencies for the app
- `avatars/` — User avatar images (PNG)
- `chatbot/` — Chatbot model, scripts, and data files
- `data/` — Reference documents and sample data
- `expenditure/` — Expenditure tracker scripts, database, and templates
- `generate_avatar/` — Scripts and assets for avatar generation
- `psychometric_test/` — Psychometric test scripts, styles, and database
- `python/` — Utility scripts and user registration DB
- `uploads/` — For user-uploaded files

## Setup Instructions

1. **Install Python 3.8+ and pip** if not already installed.
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r chatbot/requirements.txt
   ```
3. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

## Usage
- Register a new user or log in with your credentials.
- Use the sidebar to navigate between features.
- All user data is stored locally in SQLite databases or as files in this folder.
- Avatar generation is simulated by saving the uploaded image; integrate your ML model for advanced features.
- The chatbot uses a local PyTorch model and NLTK for NLP.

## Deployment Guide

### Deploy on Streamlit Cloud (via GitHub)
1. Push your project to a GitHub repository.
2. Go to [Streamlit Cloud](https://streamlit.io/cloud) and sign in with your GitHub account.
3. Click "New app", select your repository and branch, and set the main file path to `app.py`.
4. Ensure `requirements.txt` and `chatbot/requirements.txt` are present in your repo.
5. Click "Deploy". Your app will build and launch with a public URL.

### Run Locally (localhost)
1. Clone your repository:
   ```bash
   git clone https://github.com/yourusername/finedica_streamlit.git
   cd finedica_streamlit
   ```
2. Install Python 3.8+ if not already installed.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r chatbot/requirements.txt
   ```
4. Run the app:
   ```bash
   streamlit run app.py
   ```
5. Open your browser and go to `http://localhost:8501`.

---
For any issues or questions, contact the FINEDICA development team.

git add <conflicted-files>
git rebase --continue
