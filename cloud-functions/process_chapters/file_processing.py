import os
import PyPDF2
import requests
import tempfile
import multiprocessing
from google.cloud import storage
from pub_sub import publish_msg_to_topic

def extract_chapter(file_path, chapter_metadata):
    try:
        print("======================================")
        print(chapter_metadata)
        print("======================================")
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            response = requests.get(file_path)
            temp_file.write(response.content)
                
        pdf_file = open(temp_file.name, "rb")
        reader = PyPDF2.PdfReader(pdf_file)
        temp_file.close()
        
        extracted_text = ""

        start_page = chapter_metadata["child_chapter_start_page"] if "child_chapter_title" in chapter_metadata \
            else chapter_metadata["main_chapter_start_page"]

        end_page = chapter_metadata["child_chapter_end_page"] if "child_chapter_title" in chapter_metadata \
            else chapter_metadata["main_chapter_end_page"]

        for page_num in range(start_page - 1, end_page - 1):  # Page numbers are 0-based in PyPDF2
            page = reader.pages[page_num]
            extracted_text += page.extract_text()

        remove_tabs = extracted_text.replace('\t', ' ')  # Clean Tab spaces
        extracted_text = remove_tabs.replace('\n', ' ')  # Clean Newlines

        # TODO: publish the event msg to pub/sub topic make this work async and retry if failed log and store it in CloudSQL
        event_msg = {
            "bookId": chapter_metadata["bookId"],
            "chapterTitle": chapter_metadata["title_disp"] if "title_disp" in chapter_metadata else chapter_metadata["main_chapter_title"],
            "chapterText": extracted_text,
        }

        topic_id = os.environ["topic_id"]
        publish_msg_to_topic(topic_id, event_msg)

        return extracted_text
    except Exception as e:
        print("here 3")
        print(e)


def read_file_without_downloading(file_name):
    try:
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

        # Replace with your bucket name
        bucket_name = os.environ["AUDIOBRIEF_BUCKET_NAME"]

        # Retrieve the audio file from Google Cloud Storage
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)

        # Check if the file exists
        if not blob.exists():
            return {"message": "Audio file not found"}

        return blob
    except Exception as e:
        print("here 4")
        print(str(e))
    
def process_chapters_metada(file_path, chapters_metadata):
    try:
        # Create a Pool with the desired number of processes
        num_processes = int(os.environ["num_processes"])

        pool = multiprocessing.Pool(processes=num_processes)

        arg_tuples = [(file_path, chapter_metadata) for chapter_metadata in chapters_metadata]

        # Process the array elements in parallel using the pool
        results = pool.starmap(extract_chapter, arg_tuples)

        # Close the pool and wait for the work to finish
        pool.close()
        pool.join()
        
        return results
    except Exception as e:
        print("here 5")
        print(str(e))