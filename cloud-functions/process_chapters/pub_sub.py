import os
import json
from google.cloud import pubsub_v1


def publish_msg_to_topic(topic_id, msg):
    try:
        project_id = os.environ["project_id"]

        credentials = {
            "type": os.environ["type"],
            "project_id": os.environ["project_id"],
            "private_key_id": os.environ["private_key_id"],
            "private_key": os.environ["private_key"],
            "client_email": os.environ["client_email"],
            "client_id": os.environ["client_id"],
            "auth_uri": os.environ["auth_uri"],
            "token_uri": os.environ["token_uri"],
            "auth_provider_x509_cert_url": os.environ["auth_provider_x509_cert_url"],
            "client_x509_cert_url": os.environ["client_x509_cert_url"],
            "universe_domain" : os.environ["universe_domain"]
        };
        publisher = pubsub_v1.PublisherClient()

        topic_path = publisher.topic_path(project_id, topic_id)

        # Data must be a bytestring
        data = json.dumps(msg, ensure_ascii=False).encode('utf-8')

        # When you publish a message, the client returns a future.
        future = publisher.publish(topic_path, data)

        return future.result()
    except Exception as e:
        print("here 2")
        print(str(e))
