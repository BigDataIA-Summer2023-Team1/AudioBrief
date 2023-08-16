import functions_framework
from langchain import OpenAI, PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader
from langchain.chat_models import ChatOpenAI
import tiktoken
import os
from google.cloud import storage


def tiktoken_len(query):
    tokenizer = tiktoken.get_encoding('p50k_base')
    tokens = tokenizer.encode(
        query,
        disallowed_special=()
    )
    return len(tokens)

def text_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=20,
        length_function=tiktoken_len,
        separators=["\n\n", "\n", " ", ""]
    )



def write_to_blob(file_name, summary):
    bucket_name = os.environ["bucket_name"]
    
    credentials = {
    "type": os.environ["type"],
    "project_id": os.environ["project_id"],
    "private_key_id": os.environ["private_key_id"],
    "private_key": os.environ["private_key"],
    "client_email": os.environ["client_email"],
    "client_id": os.environ["client_id"],
    "auth_uri": os.environ["auth_uri"],
    "token_uri": os.environ["token_uri"],
    "auth_provider_x509_cert_url": os.environ["auth_provider_x509_cert_url"],
    "client_x509_cert_url": os.environ["client_x509_cert_url"],
    "universe_domain" : os.environ["universe_domain"]
    };

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_string(summary)