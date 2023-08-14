import os
import requests
from google.cloud import storage


def upload_file_to_gcs(local_file_path, destination_blob_name):
    try:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/opt/airflow/dags/tf-key.json" # TODO: for running in local use './tf-key.json'

        project_id = os.getenv("PROJECT_ID")
        bucket_name = os.getenv("BUCKET_NAME")

        # Initialize the Google Cloud Storage client
        client = storage.Client(project=project_id)

        # Get the bucket object
        bucket = client.get_bucket(bucket_name)

        # Create a blob object representing the file in the bucket
        blob = bucket.blob(destination_blob_name)

        # Upload the local file to the blob
        blob.upload_from_filename(local_file_path)

        print(f"File {local_file_path} uploaded to {bucket_name}/{destination_blob_name}.")

        return blob.public_url
    except Exception as e:
        print(str(e))


def download_blob(bucket_name, source_blob_name, destination_file_name):
    try:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./metadata-sql.json" # TODO:change path to '/opt/airflow/dags/tf-key.json'
        current_directory = os.getcwd()

        # List all files in the current directory
        files = os.listdir(current_directory)

        # Print the list of files
        print("here1:================================================================")
        for file in files:
            print(file)
        # Initialize the Google Cloud Storage client
        storage_client = storage.Client()

        # Get the bucket object
        bucket = storage_client.bucket(bucket_name)

        # Construct a client side representation of a blob.
        # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
        # any content from Google Cloud Storage. As we don't need additional data,
        # using `Bucket.blob` is preferred here.
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)

        print(
            "Downloaded storage object {} from bucket {} to local file {}.".format(
                source_blob_name, bucket_name, destination_file_name
            )
        )

        return read_and_delete_file("./earnings-call-data.txt")
    except Exception as e:
        print(str(e))


def download_pdf(url, local_path):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(local_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"PDF file downloaded and saved as '{local_path}'")
        else:
            print("Failed to download the PDF file")
    except Exception as e:
        print(str(e))


def delete_files_in_directory(directory_path):
    try:
        # List all files in the directory
        file_list = os.listdir(directory_path)

        # Iterate through the files and delete them
        for filename in file_list:
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
    except Exception as e:
        print(str(e))


def read_and_delete_file(file_path):
    try:
        # Read the contents of the file
        with open(file_path, "r") as file:
            file_contents = file.read()
            print("File read successfully.")

        # Delete the file
        delete_file(file_path)

        return file_contents
    except Exception as e:
        print(str(e))


def write_to_file(file_path, text):
    try:
        file = open(file_path, 'w')
        file.write(text)
        file.close()
    except Exception as e:
        print(str(e))


def delete_file(file_path):
    try:
        os.remove(file_path)
    except Exception as e:
        print(str(e))
