import base64
import json
import functions_framework
from langchain import OpenAI, PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader
from langchain.chat_models import ChatOpenAI
import tiktoken
import os
from utils import tiktoken_len, text_splitter, write_to_blob


class Document:
    def __init__(self, page_content, document_metadata={}):
        self.page_content = page_content
        self.metadata = document_metadata

# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def summarize_documents(cloud_event):
    # print("========================================================")
    # print(json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode('utf-8'))["chapterText"])
    # print("========================================================")
    chunks = text_splitter().split_text(json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode('utf-8'))["chapterText"])
    
    bookId = json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode('utf-8'))["bookId"]
    chapterTitle = json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode('utf-8'))["chapterTitle"]

    docs = [Document(page_content = chunk) for chunk in range(len(chunks))]

    refine_prompt_template = """
               write a summary of the following text in 300 words decscribing in detail about what the author penned
              """
    refine_prompt = PromptTemplate(
        template=refine_prompt_template, input_variables=[]
    )

    openai_api_key = os.environ["openai_api_key"]
    model_name = os.environ["model_name"]

    llm = ChatOpenAI(
        openai_api_key = openai_api_key,
        model_name = model_name,
        temperature = 0.0
    )

    chain = load_summarize_chain(llm, chain_type = "refine", refine_prompt = refine_prompt)
    summary = chain.run(docs)
   
    file_name = f"{bookId}/chapters/{chapterTitle}/summary.txt"

    write_to_blob(file_name, summary)
    print("========================================================")
    print(file_name)
    print("========================================================")
    
    return summary
