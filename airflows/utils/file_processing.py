import math
import PyPDF2
import multiprocessing
from pub_sub import publish_msg_to_topic


def fetch_end_page_number(reader, chapter):
    try:
        if chapter:
            if isinstance(chapter, list):
                return reader.get_destination_page_number(chapter[0])

            return reader.get_destination_page_number(chapter)
        else:
            return 0
    except Exception as e:
        print(str(e))


def fetch_book_medata(file_path):
    try:
        reader = PyPDF2.PdfReader(file_path)

        return reader.metadata
    except Exception as e:
        print(str(e))


def fetch_book_contents(bookId, file_path):
    try:
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
                                           "main_chapter_title": item.title.replace(":", "").lower().replace(" ", "-"),
                                           "main_chapter_start_page": reader.get_destination_page_number(item),
                                           "main_chapter_end_page": fetch_end_page_number(reader, next_to_next_chapter),
                                           "child_chapter_title": child_chapter.title,
                                           "title_disp": (item.title + " " + child_chapter.title).replace(":", "").replace("’","").replace(".", "").lower().replace(" ", "-"),
                                           "child_chapter_start_page": reader.get_destination_page_number(child_chapter),
                                           "child_chapter_end_page": reader.get_destination_page_number(next_chapter[
                                                                                                            child_chapter_idx + 1]) if child_chapter_idx + 1 <= no_of_child_chapters else fetch_end_page_number(
                                               reader, next_to_next_chapter)}
                                          for child_chapter_idx, child_chapter in enumerate(next_chapter)])
            else:
                if not isinstance(item, list) and next_chapter is not None:
                    chapters_metadata.append({"bookId": bookId,
                                              "main_chapter_title": item.title.replace(":", "").replace("’","").replace(".", "").lower().replace(" ", "-"),
                                              "main_chapter_start_page": reader.get_destination_page_number(item),
                                              "main_chapter_end_page": fetch_end_page_number(reader, next_chapter)})

        return chapters_metadata
    except Exception as e:
        print(str(e))


def extract_chapter(file_path, chapter_metadata):
    try:
        reader = PyPDF2.PdfReader(file_path)
        extracted_text = ""
        print("================================================================================")
        print(reader.metadata)
        print("================================================================================")

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

        topic_id = "chapters"
        publish_msg_to_topic(topic_id, event_msg)

        return extracted_text
    except Exception as e:
        print(str(e))


def process_chapters(file_path, chapters_metadata):
    try:
        # Create a Pool with the desired number of processes
        num_processes = 3
        pool = multiprocessing.Pool(processes=num_processes)

        arg_tuples = [(file_path, chapter_metadata) for chapter_metadata in chapters_metadata]

        # Process the array elements in parallel using the pool
        results = pool.starmap(extract_chapter, arg_tuples)

        # Close the pool and wait for the work to finish
        pool.close()
        pool.join()
    except Exception as e:
        print(str(e))
