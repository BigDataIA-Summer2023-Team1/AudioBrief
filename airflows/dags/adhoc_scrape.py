import os
import math
import uuid
import pandas as pd
from dotenv import load_dotenv
from datetime import timedelta

from airflow.models import DAG
from airflow.models.param import Param
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator

import sys
sys.path.append('/opt/airflow/utils/')
import cloud_sql as csql
import file_processing as fp


# from utils.cloud_sql import connect_to_sql, get_sql_client, insert_to_books_table, \
#     check_if_books_exist, insert_to_last_read_table, fetch_last_read_book_id
# from utils.file_processing import process_chapters, fetch_book_contents, fetch_book_medata


#  Create DAG to load data
user_input = {
    "file_path": "",
    "category": ""
}


def adhoc_scrape(**context):
    sql_client = csql.get_sql_client(csql.connect_to_sql)

    # TODO: download file from GCP return file path

    # process the file outline
    file_path = "./test.pdf"
    metadata = fp.fetch_book_medata(file_path)
    bookID = str(uuid.uuid4())
    books_metadata = {
        "book_id": bookID,
        "source_id": 0,
        "title": metadata["/Title"],
        "author": metadata["/Author"],
        "category": "",
        "publish": 0,
        "pages": 0,
    }

    chapters_metadata = fp.fetch_book_contents(bookID, file_path)

    # TODO: Check if we can make process_chapters step as async
    fp.process_chapters(file_path, chapters_metadata)

    csql.insert_to_books_table(sql_client, [books_metadata])


# adhoc_scrape_dag = DAG(
#     dag_id="create_table_with_indexes",
#     schedule="0 0 * * *",  # https://crontab.guru/
#     start_date=days_ago(0),
#     catchup=False,
#     dagrun_timeout=timedelta(minutes=60),
#     tags=["DAMG7245", "AudioBrief"],
#     params=user_input,
# )
#
# with adhoc_scrape_dag:
#     upload_book = PythonOperator(
#         task_id='upload_convert_book',
#         python_callable=adhoc_scrape,
#         provide_context=True,
#         dag=adhoc_scrape_dag
#     )
#
#     # Define task dependencies
#     upload_book
