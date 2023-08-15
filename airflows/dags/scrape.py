import sys
import math
import uuid
import pandas as pd
from datetime import timedelta

from airflow.models import DAG
from airflow.models.param import Param
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator



sys.path.append('/opt/airflow/utils/')
import cloud_sql as csql
import file_processing as fp
import gcs_service as gcs


def fetch_metadata(**context):
    try:
        # TODO: Fetch Last processed index
        sql_client = csql.get_sql_client(csql.connect_to_sql)
        last_read_index = csql.fetch_last_read_book_id(sql_client)

        dataset_path = "https://raw.githubusercontent.com/BigDataIA-Summer2023-Team1/project/main/test-data.csv"
        data = pd.read_csv(dataset_path, skiprows=last_read_index)

        no_of_records = len(data)
        last_row_to_process = data['ID'].iloc[-1]

        context['ti'].xcom_push(key="metadata",
                                value={"last_read_index": last_read_index, "no_of_records": no_of_records,
                                       "last_row_to_process": last_row_to_process})

    except Exception as e:
        msg = str(e)


def data_extraction(pipeline_no, **context):
    try:
        no_of_pipelines = context['params']['no_of_pipelines']

        metadata = context["ti"].xcom_pull(key="metadata", task_ids="read_metadata",
                                           dag_id="scrape_books_and_extract_chapters_and_load")

        dataset_path = "https://raw.githubusercontent.com/BigDataIA-Summer2023-Team1/project/main/test-data.csv"
        # data = pd.read_csv(dataset_path, skiprows=metadata["last_read_index"])
        data = pd.read_csv(dataset_path)

        data_per_pipeline = math.ceil(metadata["no_of_records"] / no_of_pipelines)
        data = data[(pipeline_no - 1) * data_per_pipeline:pipeline_no * data_per_pipeline]
        print("Data here: ", data)

        sql_client = csql.get_sql_client(csql.connect_to_sql)

        books_metadata = []
        for index, row in data.iterrows():
            bookID = str(uuid.uuid4())
            book_metadata = {
                "book_id": bookID,
                "source_id": row["ID"],
                "title": row["Title"] if row["Title"] else "",
                "author": row["Author"] if row["Author"] else "",
                "category": row["Category"] if row["Category"] else "",
                "publish": row["Publish"] if row["Publish"] else 0,
                "pages": row["Page"] if row["Page"] else 0,
                "url": row["URL"] if row["URL"] else "",
            }
            books_metadata.append(book_metadata)

            # TODO: check if required fields are present in raw data
            books_exists = csql.check_if_books_exist(sql_client, {"sourceId": row["ID"], "title": row["Title"]})
            if books_exists:
                return
                # TODO: Log and raise exception that file already processed

            # TODO: download file from GCP return file path
            file_path = f"./books/{row['Title']}.pdf"
            gcs.download_pdf(row["URL"], file_path)

            chapters_metadata = fp.fetch_book_contents(bookID, file_path)
            chapters = [chapter["title_disp"] if "title_disp" in chapter else chapter["main_chapter_title"] for
                        chapter in chapters_metadata]
            chapters = f"{chapters}"
            book_metadata["chapters"] = chapters

            # TODO: Check if we can make process_chapters step as async
            # Method -1
            # fp.process_chapters(book_metadata["url"], chapters_metadata)

            # Method -2
            for chapter_metadata in chapters_metadata:
                fp.extract_chapter(file_path, chapter_metadata)

            # Method -3: Trigger cloud function
            chapters_metadata = [chapters_metadata[8]]
            # payload = {
            #     "file_path": book_metadata["url"],
            #     "chapters_metadata": chapters_metadata
            # }
            # print("Payload: ============================================================")
            # print(payload)
            # print("============================================================")
            # headers = {"Content-Type": "application/json"}
            # resp = requests.post("https://us-east1-audiobrief.cloudfunctions.net/process_chapters",
            #                      data=json.dumps(payload), headers=headers)
            # if resp.status_code == 200:
            #     print(resp)
            # else:
            #     print("failed process")

            # Method -4:
            # context['ti'].xcom_push(key=subtask_id, value={"file_path": file_path,
            #                                                "book_metadata": book_metadata,
            #                                                "chapters_metadata": chapters_metadata})

            # Method -5:
            # trigger_task = TriggerDagRunOperator(
            #     task_id=bookID,
            #     trigger_dag_id='trigger_parallel_processing_dag',  # Name of the separate DAG
            #     conf={"file_path": file_path, "book_metadata": book_metadata, "chapters_metadata": chapters_metadata},
            #     dag=scrape_dag,
            # )

        # TODO: send async bulk event to store books metadata in cloud sql and log for any errors
        csql.insert_to_books_table(sql_client, books_metadata)

    except Exception as e:
        msg = str(e)


def process_chapters_in_pipeline(subtask_pipeline_no, **context):
    try:
        no_of_threads = 3

        # metadata = context['ti'].xcom_pull(task_ids="extract_chapters_list", key=subtask_id)
        chapters_metadata = context['dag_run'].conf.get('chapters_metadata')
        file_path = context['dag_run'].conf.get('file_path')

        no_of_chapters_per_pipeline = math.ceil(len(chapters_metadata) / no_of_threads)

        chapters_metadata = chapters_metadata[(subtask_pipeline_no - 1) * no_of_chapters_per_pipeline:subtask_pipeline_no * no_of_chapters_per_pipeline]

        for chapter_metadata in chapters_metadata:
            fp.extract_chapter(file_path, chapter_metadata)
    except Exception as e:
        msg = str(e)


def update_books_metadata(subtask_id, **context):
    try:
        metadata = context["ti"].xcom_pull(task_ids="extract_chapters_list", key=subtask_id)
        sql_client = csql.get_sql_client(csql.connect_to_sql)
        csql.insert_to_books_table(sql_client, metadata["books_metadata"])
    except Exception as e:
        msg = str(e)


def update_metadata(**context):
    try:
        # TODO: Update Last processed index
        metadata = context['ti'].xcom_pull(task_ids="extract_chapters_list", key='metadata')
        sql_client = csql.get_sql_client(csql.connect_to_sql)

        csql.insert_to_last_read_table(sql_client, {"source_id": metadata["last_row_to_process"]})

        # TODO: Delete processed books
        gcs.delete_files_in_directory("./books")
    except Exception as e:
        msg = str(e)


# def create_subdag(parent_dag_name, child_dag_name, pipeline_no, args):
#     dag_subdag = DAG(
#         dag_id=f'{parent_dag_name}.{child_dag_name}',
#         schedule=None,  # Set to None if you want to trigger manually
#         start_date=days_ago(0),
#         catchup=False,
#         dagrun_timeout=timedelta(minutes=60),
#         params=args,
#     )
#
#     with dag_subdag:
#         step_1 = PythonOperator(
#             task_id='extract_chapters_list',
#             python_callable=data_extraction,
#             provide_context=True,
#             op_kwargs={"pipeline_no": pipeline_no, "subtask_id": f'{parent_dag_name}-{child_dag_name}'},
#             dag=dag_subdag
#         )
#
#         step_2 = PythonOperator(
#             task_id='step_2',
#             python_callable=process_chapters_in_pipeline,
#             provide_context=True,
#             op_kwargs={"subtask_pipeline_no": 1, "subtask_id": f'{parent_dag_name}-{child_dag_name}'},
#             dag=dag_subdag
#         )
#
#         step_3 = PythonOperator(
#             task_id='step_3',
#             python_callable=process_chapters_in_pipeline,
#             provide_context=True,
#             op_kwargs={"subtask_pipeline_no": 2, "subtask_id": f'{parent_dag_name}-{child_dag_name}'},
#             dag=dag_subdag
#         )
#
#         step_4 = PythonOperator(
#             task_id='step_4',
#             python_callable=process_chapters_in_pipeline,
#             provide_context=True,
#             op_kwargs={"subtask_pipeline_no": 3, "subtask_id": f'{parent_dag_name}-{child_dag_name}'},
#             dag=dag_subdag
#         )
#
#         step_5 = PythonOperator(
#             task_id='step_5',
#             python_callable=update_books_metadata,
#             provide_context=True,
#             op_kwargs={"subtask_id": f'{parent_dag_name}-{child_dag_name}'},
#             dag=dag_subdag
#         )
#
#         # step_6 = PythonOperator(
#         #     task_id='step_6',
#         #     python_callable=update_books_metadata,
#         #     provide_context=True,
#         #     op_kwargs={"subtask_id": f'{parent_dag_name}-{child_dag_name}'},
#         #     dag=dag_subdag
#         # )
#         # step_7 = PythonOperator(
#         #     task_id='step_7',
#         #     python_callable=update_books_metadata,
#         #     provide_context=True,
#         #     op_kwargs={"subtask_id": f'{parent_dag_name}-{child_dag_name}'},
#         #     dag=dag_subdag
#         # )
#
#         step_1 >> step_2 >> step_5
#         # step_1 >> step_3 >> step_6
#         # step_1 >> step_4 >> step_7
#
#     return dag_subdag


#  Create DAG to load data
user_input = {
    "no_of_records_to_read_daily": Param(default=5, type='number'),
    "no_of_pipelines": Param(default=4, type='number'),
    "no_of_threads": Param(default=3, type='number'),
}

# trigger_parallel_processing_dag = DAG(
#     dag_id='trigger_parallel_processing_dag',
#     schedule_interval=None,  # You might want to set this based on your needs
#     start_date=days_ago(0),
#     catchup=False,
#     params=user_input,
# )
#
# with trigger_parallel_processing_dag:
#     step_1 = PythonOperator(
#         task_id='step_2',
#         python_callable=process_chapters_in_pipeline,
#         provide_context=True,
#         op_kwargs={"subtask_pipeline_no": 1},
#         dag=trigger_parallel_processing_dag
#     )
#
#     step_2 = PythonOperator(
#         task_id='step_3',
#         python_callable=process_chapters_in_pipeline,
#         provide_context=True,
#         op_kwargs={"subtask_pipeline_no": 2},
#         dag=trigger_parallel_processing_dag
#     )
#
#     step_3 = PythonOperator(
#         task_id='step_4',
#         python_callable=process_chapters_in_pipeline,
#         provide_context=True,
#         op_kwargs={"subtask_pipeline_no": 3},
#         dag=trigger_parallel_processing_dag
#     )
#
#     step_1, step_2, step_3

scrape_dag = DAG(
    dag_id="scrape_books_and_extract_chapters_and_load",
    schedule="0 0 * * *",  # https://crontab.guru/
    start_date=days_ago(0),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["DAMG7245", "AudioBrief"],
    params=user_input,
)

with scrape_dag:
    read_metadata = PythonOperator(
        task_id='read_metadata',
        python_callable=fetch_metadata,
        provide_context=True,
        dag=scrape_dag
    )

    # pipeline_1 = PythonOperator(
    #     task_id='pipeline_1_process_files',
    #     python_callable=data_extraction,
    #     provide_context=True,
    #     op_kwargs={"pipeline_no": 1},
    #     dag=scrape_dag
    # )

    # pipeline_1 = SubDagOperator(
    #     task_id='pipeline_1_process_files',
    #     subdag=create_subdag('scrape_books_and_extract_chapters_and_load', 'pipeline_1_process_files', 1, user_input),
    #     dag=scrape_dag
    # )

    pipeline_1 = PythonOperator(
        task_id='pipeline_1_process_files',
        python_callable=data_extraction,
        provide_context=True,
        op_kwargs={"pipeline_no": 1},
        dag=scrape_dag
    )

    modify_metadata = PythonOperator(
        task_id='update_metadata',
        python_callable=update_metadata,
        dag=scrape_dag,
        provide_context=True,
    )

    # Define task dependencies
    read_metadata >> [pipeline_1] >> modify_metadata
