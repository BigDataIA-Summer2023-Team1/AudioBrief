import os
import json
import base64
import functions_framework
from google.cloud import texttospeech


# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def synthesize_long_audio(cloud_event):
    # Print out the data from Pub/Sub, to prove that it worked
    print("=======================================================")
    print("audio conversion")
    print(base64.b64decode(cloud_event.data["message"]["data"]))
    print("=======================================================")

    voiceType = "en-US-Standard-A"  #os.environ["voice_type"]
    chapterText = json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode('utf-8'))["chapterText"]
    bookId = json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode('utf-8'))["bookId"]
    chapterTitle = json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode('utf-8'))["chapterTitle"]

    

    project_id = os.environ["project_id"]
    location =  os.environ["location"]
    bucket_name = os.environ["bucket_name"]

    output_gcs_uri = f"gs://{bucket_name}/{bookId}/chapters/{chapterTitle}/audio.mp3"
    print(output_gcs_uri)

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

    client = texttospeech.TextToSpeechLongAudioSynthesizeClient()

    textInput = texttospeech.SynthesisInput(
        text = chapterText
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", name=voiceType
    )

    parent = f"projects/{project_id}/locations/{location}"

    request = texttospeech.SynthesizeLongAudioRequest(
        parent=parent,
        input=textInput,
        audio_config=audio_config,
        voice=voice,
        output_gcs_uri=output_gcs_uri,
    )

    operation = client.synthesize_long_audio(request=request)
    # Set a deadline for your LRO to finish. 300 seconds is reasonable, but can be adjusted depending on the length of the input.
    # If the operation times out, that likely means there was an error. In that case, inspect the error, and try again.
    result = operation.result(timeout=300)
    print(
        "\nFinished processing, check your GCS bucket to find your audio file! Printing what should be an empty result: ",
        result,
    )

    return
