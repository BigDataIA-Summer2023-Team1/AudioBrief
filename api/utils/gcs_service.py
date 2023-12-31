import os
from google.cloud import storage


def read_text_file_without_downloading(file_name):
    try:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "./utils/metadata-sql.json"

        storage_client = storage.Client()

        # Replace with your bucket name
        bucket_name = os.environ["AUDIOBRIEF_BUCKET_NAME"]

        # Retrieve the audio file from Google Cloud Storage
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)

        chunks = []
        with blob.open("r") as file_stream:
            while True:
                chunk = file_stream.read(1024)  # Read 1024 bytes at a time
                if not chunk:
                    break
                chunks.append(chunk)
            return " ".join(chunks)
    except Exception as e:
        print(str(e))


def read_audio_file_without_downloading(file_name):
    try:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "./utils/metadata-sql.json"

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
        print(str(e))
