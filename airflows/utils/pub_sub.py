import os
import json
from google.cloud import pubsub_v1


def publish_msg_to_topic(topic_id, msg):
    try:
        project_id = "audiobrief"

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./publish-message-to-topic.json"
        publisher = pubsub_v1.PublisherClient()

        topic_path = publisher.topic_path(project_id, topic_id)

        # Data must be a bytestring
        data = json.dumps(msg, ensure_ascii=False).encode('utf-8')

        # When you publish a message, the client returns a future.
        future = publisher.publish(topic_path, data)

        return future.result()
    except Exception as e:
        print(str(e))
