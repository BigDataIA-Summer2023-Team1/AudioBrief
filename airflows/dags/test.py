import math
import uuid
import PyPDF2
import pandas as pd
import multiprocessing
from airflows.utils.pub_sub import publish_msg_to_topic
from airflows.utils.cloud_sql import connect_to_sql, get_sql_client, insert_to_books_table, \
    check_if_books_exist, insert_to_last_read_table, fetch_last_read_book_id


def fetch_end_page_number(reader, chapter):
    if chapter:
        if isinstance(chapter, list):
            return reader.get_destination_page_number(chapter[0])

        return reader.get_destination_page_number(chapter)
    else:
        return 0


def fetch_book_contents(bookId, file_path):
    reader = PyPDF2.PdfReader(file_path)
    bookmark_list = reader.outline

    chapters_metadata = []
    no_of_chapters = len(bookmark_list) - 1

    for i, item in enumerate(bookmark_list):
        next_chapter = bookmark_list[i + 1] if i + 1 <= no_of_chapters else None
        next_to_next_chapter = bookmark_list[i + 2] if i + 2 <= no_of_chapters else None

        if next_chapter is not None and isinstance(next_chapter, list):
            no_of_child_chapters = len(next_chapter) - 1

            chapters_metadata.extend([{"bookId": bookId,
                                       "main_chapter_title": item.title,
                                       "main_chapter_start_page": reader.get_destination_page_number(item),
                                       "main_chapter_end_page": fetch_end_page_number(reader, next_to_next_chapter),
                                       "child_chapter_title": child_chapter.title,
                                       "title_disp": item.title + " " + child_chapter.title,
                                       "child_chapter_start_page": reader.get_destination_page_number(child_chapter),
                                       "child_chapter_end_page": reader.get_destination_page_number(next_chapter[
                                                                                                        child_chapter_idx + 1]) if child_chapter_idx + 1 <= no_of_child_chapters else fetch_end_page_number(
                                           reader, next_to_next_chapter)}
                                      for child_chapter_idx, child_chapter in enumerate(next_chapter)])
        else:
            if not isinstance(item, list) and next_chapter is not None:
                chapters_metadata.append({"bookId": bookId,
                                          "main_chapter_title": item.title,
                                          "main_chapter_start_page": reader.get_destination_page_number(item),
                                          "main_chapter_end_page": fetch_end_page_number(reader, next_chapter)})

    return chapters_metadata


def extract_chapter(file_path, chapter_metadata):
    reader = PyPDF2.PdfReader(file_path)
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

    topic_id = "books-chapters"
    # publish_msg_to_topic(topic_id, event_msg)

    return extracted_text


def process_chapters(file_path, chapters_metadata):
    # Create a Pool with the desired number of processes
    num_processes = 3
    pool = multiprocessing.Pool(processes=num_processes)

    arg_tuples = [(file_path, chapter_metadata) for chapter_metadata in chapters_metadata]

    # Process the array elements in parallel using the pool
    results = pool.starmap(extract_chapter, arg_tuples)

    # Close the pool and wait for the work to finish
    pool.close()
    pool.join()


def scrape_data():
    # TODO: Fetch Last processed index
    sql_client = get_sql_client(connect_to_sql)
    last_read_index = fetch_last_read_book_id(sql_client)

    no_of_pipelines = 4
    pipeline_no = 1

    dataset_path = "https://raw.githubusercontent.com/BigDataIA-Summer2023-Team1/project/main/test-data.csv"
    data = pd.read_csv(dataset_path, skiprows=last_read_index)

    no_of_records = len(data)
    last_row_to_process = data['ID'].iloc[-1]

    data_per_pipeline = math.ceil(no_of_records / no_of_pipelines)
    data = data[(pipeline_no - 1) * data_per_pipeline:pipeline_no * data_per_pipeline]

    books_metadata = []
    for index, row in data.iterrows():
        bookID = str(uuid.uuid4())
        books_metadata.append({
            "book_id": bookID,
            "source_id": row["ID"],
            "title": "" if row["Title"] is float('nan') else row["Title"],
            "author": "" if row["Author"] is float('nan') else row["Author"],
            "category": "" if row["Category"] is float('nan') else row["Category"],
            "publish": 0 if row["Publish"] is float('nan') else row["Publish"],
            "pages": 0 if row["Page"] is float('nan') else row["Page"],
        })

        # TODO: check if required fields are present in raw data

        books_exists = check_if_books_exist(sql_client, {"sourceId": row["ID"], "title": row["Title"]})
        if not books_exists:
            pass
            # TODO: Log and raise exception that file already processed

        # TODO: download file from GCP return file path

        # process the file outline
        file_path = "./test.pdf"
        chapters_metadata = fetch_book_contents(bookID, file_path)

        # TODO: Check if we can make process_chapters step as async
        process_chapters(file_path, chapters_metadata)

    # TODO: send async bulk event to store books metadata in cloud sql and log for any errors
    insert_to_books_table(sql_client, books_metadata)

    # TODO: Update Last processed index
    insert_to_last_read_table(sql_client, {"source_id": last_row_to_process})

    # TODO: Delete processed files


if __name__ == '__main__':
    scrape_data()

