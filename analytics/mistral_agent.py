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

df = pd.DataFrame({
    "Имя": ["Алиса", "Боб", "Чарли"],
    "Возраст": [30, 25, 35],
    "Город": ["Москва", "Питер", "Казань"],
    "Зарплата": [120000, 95000, 140000]
})

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