import os
import webbrowser
from getpass import getpass
from urllib.parse import parse_qs
from dotenv import load_dotenv
from requests_oauthlib import OAuth1Session
from datetime import date, timedelta
import pandas as pd
import numpy as np
from mistralai import Mistral
import gradio as gr
from transformers import pipeline

load_dotenv() # Илливилли шпилли-вилли факинг пис оф арт проджект эмэйзинг абсолютли горджеус Австралия

CLIENT_ID = os.getenv('ConsumerKey')
CLIENT_SECRET = os.getenv('ConsumerSecret')

def parse_token(text):
    data = parse_qs(text)
    return (data.get('oauth_token', [None])[0], data.get('oauth_token_secret', [None])[0])

session = OAuth1Session(CLIENT_ID, CLIENT_SECRET, callback_uri='oob', signature_type='BODY')
resp = session.post('https://authentication.fatsecret.com/oauth/request_token')
resp.raise_for_status()
request_token, request_token_secret = parse_token(resp.text)

auth_url = f'https://authentication.fatsecret.com/oauth/authorize?oauth_token={request_token}'
webbrowser.open(auth_url)
verifier = getpass('Введите PIN-код: ').strip()

access_session = OAuth1Session(CLIENT_ID, CLIENT_SECRET, resource_owner_key=request_token, resource_owner_secret=request_token_secret, verifier=verifier, signature_type='BODY')
resp = access_session.post('https://authentication.fatsecret.com/oauth/access_token')
resp.raise_for_status()
access_token, access_token_secret = parse_token(resp.text)

api_session = OAuth1Session(CLIENT_ID, CLIENT_SECRET, resource_owner_key=access_token, resource_owner_secret=access_token_secret)

def date_to_int(d):
    return (d - date(1970, 1, 1)).days

target_days = date_to_int(date(2026, 4, 1))

response = api_session.get(
    'https://platform.fatsecret.com/rest/server.api',
    params={'method': 'food_entries.get.v2', 'format': 'json', 'date': target_days}
)
response.raise_for_status()

food_entries = response.json()['food_entries']['food_entry']
if isinstance(food_entries, dict):
    food_entries = [food_entries]
df = pd.DataFrame(food_entries)

def int_to_date(days):
    return (date(1970, 1, 1) + timedelta(days=int(days))).isoformat()

def make_docs(dataframe):
    docs = []
    for _, row in dataframe.iterrows():
        desc = f"Прием пищи: {row.get('food_entry_name', '')}, блюдо: {row.get('food_name', '')}, калории: {row.get('calories', '')} ккал, белки: {row.get('protein', '')} г, жиры: {row.get('fat', '')} г, углеводы: {row.get('carbohydrate', '')} г, порция: {row.get('serving_size', '')}, дата: {int_to_date(row.get('date_int', 0))}"
        docs.append(desc)
    return docs

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
EMBED_MODEL = "mistral-embed"
CHAT_MODEL = "mistral-small"

documents = make_docs(df)

def embed(texts):
    resp = client.embeddings.create(model=EMBED_MODEL, inputs=texts)
    return np.array([d.embedding for d in resp.data])

doc_embeddings = embed(documents)

tqa_pipeline = pipeline("table-question-answering", model="google/tapas-base-finetuned-wtq")

def retrieve(query, top_k=10):
    q_emb = embed([query])[0]
    scores = np.dot(doc_embeddings, q_emb)
    best_idx = np.argsort(scores)[-top_k:][::-1]
    return best_idx, [documents[i] for i in best_idx]

def table_qa(query, df_subset):
    if df_subset.empty:
        return None
    table = {col: df_subset[col].astype(str).tolist() for col in df_subset.columns}
    result = tqa_pipeline(query=query, table=table)
    ans = result.get('answer', '')
    return ans if ans and ans != 'None' else None

def chat(message, history):
    best_idx, retrieved_docs = retrieve(message)
    df_subset = df.iloc[best_idx]
    tqa_answer = table_qa(message, df_subset)

    context = ""
    if tqa_answer:
        context += f"Точный ответ анализа таблицы: {tqa_answer}\n\n"
    context += "Данные:\n" + "\n".join(retrieved_docs)

    system_msg = f"Ты помощник по питанию. Используй предоставленный контекст для ответа.\n\n{context}"
    messages = [{"role": "system", "content": system_msg}]
    for human_msg, ai_msg in history:
        messages.append({"role": "user", "content": human_msg})
        messages.append({"role": "assistant", "content": ai_msg})
    messages.append({"role": "user", "content": message})

    response = client.chat.complete(model=CHAT_MODEL, messages=messages)
    return response.choices[0].message.content

gr.ChatInterface(chat).launch()