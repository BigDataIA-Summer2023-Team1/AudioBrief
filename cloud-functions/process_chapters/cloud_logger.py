import os
from google.cloud import logging as gcl


def logger():
    try:
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
        client = gcl.Client()

        client.setup_logging()

        log_name = os.environ["log_name"]

        return client.logger(log_name)
    except Exception as e:
        print("here 6")
        print(str(e))
