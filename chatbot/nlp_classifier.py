import json
import os
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as palm

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / 'chatbot_data.json'

if DATA_FILE.exists():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        LOCAL_QA = json.load(f)
else:
    LOCAL_QA = {}

vectorizer = TfidfVectorizer().fit(list(LOCAL_QA.keys()) or [''])
data_vecs = vectorizer.transform(list(LOCAL_QA.keys()) or [''])

def get_local_answer(question: str):
    if not LOCAL_QA:
        return None
    vec = vectorizer.transform([question])
    sims = cosine_similarity(vec, data_vecs).ravel()
    best_idx = sims.argmax()
    if sims[best_idx] >= 0.35:
        return LOCAL_QA[list(LOCAL_QA.keys())[best_idx]]
    return None

def call_palm(question: str):
    palm.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    try:
        response = palm.chat(messages=[question])
        if response and response.last:
            return response.last
    except Exception:
        pass
    return "Sorry, I don't have the information right now."
