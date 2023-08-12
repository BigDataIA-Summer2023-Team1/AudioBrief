import os
from google.cloud import storage


def upload_file_to_gcs(local_file_path, destination_blob_name):
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


def download_blob(bucket_name, source_blob_name, destination_file_name):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/opt/airflow/dags/tf-key.json" # TODO:change path to '/opt/airflow/dags/tf-key.json'

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


def read_and_delete_file(file_path):
    # Read the contents of the file
    with open(file_path, "r") as file:
        file_contents = file.read()
        print("File read successfully.")

    # Delete the file
    delete_file(file_path)
    print("File deleted successfully.")

    return file_contents


def write_to_file(file_path, text):
    file = open(file_path, 'w')
    file.write(text)
    file.close()


def delete_file(file_path):
    os.remove(file_path)
