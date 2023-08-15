import sys
import uuid
import datetime
from datetime import timedelta

from airflow.models import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator

sys.path.append('/opt/airflow/utils/')
import cloud_sql as csql
import file_processing as fp
import gcs_service as gcs


#  Create DAG to load data
user_input = {
    "file_path": "",
    "category": ""
}


def adhoc_scrape(**context):
    sql_client = csql.get_sql_client(csql.connect_to_sql)

    # TODO: download file from GCP return file path
    params = context['dag_run'].conf
    file_path = params.get("file_path")

    local_file_path = f"./books/{datetime.datetime.now()}.pdf"
    gcs.download_pdf(file_path, local_file_path)

    metadata = fp.fetch_book_medata(local_file_path)
    bookID = str(uuid.uuid4())
    books_metadata = {
        "book_id": bookID,
        "source_id": 0,
        "title": metadata["/Title"],
        "author": metadata["/Author"],
        "category": "",
        "publish": 0,
        "pages": 0,
        "url": file_path,
    }

    chapters_metadata = fp.fetch_book_contents(bookID, local_file_path)
    chapters = [chapter["title_disp"] if "title_disp" in chapter else chapter["main_chapter_title"] for
                chapter in chapters_metadata]
    chapters = f"{chapters}"
    books_metadata["chapters"] = chapters

    books_exists = csql.check_if_books_exist(sql_client, {"sourceId": "", "title": books_metadata["title"]})
    if books_exists:
        return

    # TODO: Check if we can make process_chapters step as async
    for chapter_metadata in chapters_metadata:
        fp.extract_chapter(local_file_path, chapter_metadata)

    csql.insert_to_books_table(sql_client, [books_metadata])

    gcs.delete_files_in_directory("./books")


adhoc_scrape_dag = DAG(
    dag_id="file_upload_dag",
    schedule=None,  # https://crontab.guru/
    start_date=days_ago(0),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["DAMG7245", "AudioBrief"],
    params=user_input,
)

with adhoc_scrape_dag:
    upload_book = PythonOperator(
        task_id='upload_convert_book',
        python_callable=adhoc_scrape,
        provide_context=True,
        dag=adhoc_scrape_dag
    )

    # Define task dependencies
    upload_book
