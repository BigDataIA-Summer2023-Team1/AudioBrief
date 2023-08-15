import os
import ast
import json
import base64
import requests
import streamlit as st
from google.cloud import storage

st.title('Final Project')


FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000/api/v1")


# Adhoc File upload
uploaded_file = st.file_uploader("Upload book to summarize")
if uploaded_file:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "./metadata-sql.json"

    storage_client = storage.Client()
    bucket = storage_client.bucket("audiobrief-books")
    blob = bucket.blob(uploaded_file.name)

    content_type = "application/pdf"
    blob.upload_from_file(uploaded_file, content_type=content_type)

    pdf_url = blob.public_url
    print(pdf_url)

    airflow_trigger = os.getenv("AIRFLOW_TRIGGER", "http://localhost:8080/api/v1/dags/file_upload_dag/dagRuns")
    username = os.getenv("AIRFLOW_USER", "airflow")
    password = os.getenv("AIRFLOW_PASSWORD", "airflow")

    credentials = f"{username}:{password}"
    base_auth_token = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    payload = json.dumps({"conf": {"file_path": pdf_url}})
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Basic {base_auth_token}"
    }

    response = requests.request("POST", airflow_trigger, headers=headers, data=payload)
    if response.status_code == 200:
        st.write("Successfully triggered the airflow pipeline.")
    else:
        st.write("Failed to upload file.")


access_token = st.session_state["access_token"]
headers = {"Authorization": f"Bearer {access_token}"}

books = []
book_names = []
books_response = requests.get(f"{FASTAPI_URL}/books", headers=headers)
if books_response.status_code == 200:
    books = books_response.json()
    book_names = [book["title"] for book in books]

book = st.selectbox('Book Name', book_names)

selected_book = list(filter(lambda obj: obj.get("title") == book, books))
selected_book_chapters = selected_book[0]["chapters"][1:-1]
parsed_selected_book_chapters = ast.literal_eval("[" + selected_book_chapters + "]")


chapter = st.selectbox('Chapters', parsed_selected_book_chapters)

summarize_btn = st.button('Summarize as Text')
audio_btn = st.button('Generate Audio')
if summarize_btn:
    bookId = selected_book[0]["id"]
    # chapter = "4321"

    headers = {"Authorization": f"Bearer {access_token}"}
    summary_response = requests.get(f"{FASTAPI_URL}/books/{bookId}/chapters/{chapter}/summarize", headers=headers)
    if summary_response.status_code == 200:
        summary = summary_response.json()["summary"]
        st.write(summary)

if audio_btn:
    bookId = selected_book[0]["id"]
    # chapter = "4321"

    headers = {"Authorization": f"Bearer {access_token}"}
    audio_response = requests.get(f"{FASTAPI_URL}/books/{bookId}/chapters/{chapter}/audio", headers=headers)
    if audio_response.status_code == 200:
        st.audio(audio_response.content, format="audio/mp3")