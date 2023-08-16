import os
import functions_framework
from file_processing import extract_chapter, process_chapters_metada

@functions_framework.http
def process_chapters(request):
    try:
        # Create a Pool with the desired number of processes
        num_processes = int(os.environ["num_processes"])
        request_json = request.get_json(silent=True)
        
        if request_json and 'file_path' not in request_json:
            # log it 
            return
        
        if request_json and 'chapters_metadata' not in request_json:
            # log it 
            return 
            
        file_path = request_json["file_path"]
        chapters_metadata = request_json["chapters_metadata"]
        print("===============================================")
        print("file_path: ", file_path)
        print("chapters_metadata: ", chapters_metadata)
        print("===============================================")

        results = process_chapters_metada(file_path, chapters_metadata)

        return {"status": "started processing chapters"}
    except Exception as e:
        print("here 1")
        print(str(e))
