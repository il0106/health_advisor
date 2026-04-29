import os
import webbrowser
from getpass import getpass
from urllib.parse import parse_qs
from dotenv import load_dotenv
from requests_oauthlib import OAuth1Session
from datetime import date
import pandas as pd


load_dotenv()
CLIENT_ID = os.getenv('ConsumerKey')
CLIENT_SECRET = os.getenv('ConsumerSecret')

def parse_token(text):
    data = parse_qs(text)
    return (data.get('oauth_token', [None])[0],
            data.get('oauth_token_secret', [None])[0])

session = OAuth1Session(CLIENT_ID, CLIENT_SECRET, callback_uri='oob', signature_type='BODY')
resp = session.post('https://authentication.fatsecret.com/oauth/request_token')
resp.raise_for_status()
request_token, request_token_secret = parse_token(resp.text)

auth_url = f'https://authentication.fatsecret.com/oauth/authorize?oauth_token={request_token}'
# print(f'Перейдите по ссылке и разрешите доступ:\n{auth_url}')
webbrowser.open(auth_url)

verifier = getpass('Введите PIN-код: ').strip()

access_session = OAuth1Session(
    CLIENT_ID, CLIENT_SECRET,
    resource_owner_key=request_token,
    resource_owner_secret=request_token_secret,
    verifier=verifier,
    signature_type='BODY'
)
resp = access_session.post('https://authentication.fatsecret.com/oauth/access_token')
resp.raise_for_status()
access_token, access_token_secret = parse_token(resp.text)

api_session = OAuth1Session(
    CLIENT_ID, CLIENT_SECRET,
    resource_owner_key=access_token,
    resource_owner_secret=access_token_secret
)
response = api_session.get(
    'https://platform.fatsecret.com/rest/server.api',
    params={'method': 'profile.get', 'format': 'json'}
)
response.raise_for_status()


def date_to_int(d):
    epoch = date(1970, 1, 1)
    return (d - epoch).days

date = date_to_int(date(2026, 4, 1))


response = api_session.get(
    'https://platform.fatsecret.com/rest/server.api',
    params={'method': 'food_entries.get.v2', 
            'format': 'json',
            'date': date}
)
response.raise_for_status()

df = pd.DataFrame(response.json()['food_entries']['food_entry'])



from mistralai import Mistral
from dotenv import load_dotenv
import os
import gradio as gr
import pandas as pd
import numpy as np


load_dotenv()
client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
EMBED_MODEL = "mistral-embed"
CHAT_MODEL = "mistral-small"

def make_docs(dataframe):
    docs = []
    for i, row in dataframe.iterrows():
        cols = ", ".join([f"{col}: {val}" for col, val in row.items()])
        docs.append(f"Строка {i+1}: {cols}")
    return docs

documents = make_docs(df)

def embed(texts):
    resp = client.embeddings.create(model=EMBED_MODEL, inputs=texts)
    return np.array([d.embedding for d in resp.data])

doc_embeddings = embed(documents)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def retrieve(query, top_k=2):
    q_emb = embed([query])[0]
    scores = [cosine_similarity(q_emb, doc_emb) for doc_emb in doc_embeddings]
    best_idx = np.argsort(scores)[-top_k:][::-1]
    return [documents[i] for i in best_idx]

def chat(message, history):
    retrieved = retrieve(message)
    context = "\n".join(retrieved)
    system_msg = f"Ты помощник по данным. Используй только эти данные для ответа:\n{context}"

    messages = [{"role": "system", "content": system_msg}]
    for human_msg, ai_msg in history:
        messages.append({"role": "user", "content": human_msg})
        messages.append({"role": "assistant", "content": ai_msg})
    messages.append({"role": "user", "content": message})

    response = client.chat.complete(model=CHAT_MODEL, messages=messages)
    return response.choices[0].message.content

gr.ChatInterface(chat).launch()
