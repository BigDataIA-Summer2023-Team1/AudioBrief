import os
from google.cloud import logging as gcl


def logger():
    try:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "./utils/metadata-sql.json"
        client = gcl.Client()

        client.setup_logging()

        return client.logger('audio-brief-logger')
    except Exception as e:
        print(str(e))
