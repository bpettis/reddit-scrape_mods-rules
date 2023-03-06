#! /usr/bin/python3

import praw, os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv, find_dotenv
from google.cloud import storage
import google.cloud.logging

# set up some global variables:
reddit = praw.Reddit("modscraper")

# enable/disable google cloud storage
use_gcs = True

# load environment variables
load_dotenv(find_dotenv())
bucket_name = os.environ.get("GCS_BUCKET_NAME")
project_id = os.environ.get("GCP_PROJECT")
log_name = os.environ.get("LOG_ID")


# Set up Google cloud logging:
log_client = google.cloud.logging.Client(project=project_id)
logger = log_client.logger(name=log_name)

def get_subreddits():
    subreddit_list = []
    with open("subreddits.txt", "r") as file:
        data = file.read()
        subreddit_list = data.split("\n")
    return subreddit_list

def csv_setup(sub):
    today = datetime.today().strftime('%Y-%m-%d')
    Path("output/" + today + "/sidebars").mkdir(parents=True, exist_ok=True)
    filename = "output/" + today + "/sidebars/" + sub + ".txt"
    with open(filename, 'w') as file:
        file.write('Sidebar for /r/' + sub + '\n\n')
    print(f'Created {filename} for /r/{sub}')
    return filename

def get_sidebars(sub, output):
    id_card = reddit.subreddit(sub).widgets.id_card
    with open(output, "a") as file:
        file.write(str(id_card.subscribersCount) + ' ' + id_card.subscribersText + '\n\n')
        file.write(id_card.description + '\n\n')
    widgets = reddit.subreddit(sub).widgets.sidebar
    for widget in widgets:
        if isinstance(widget, praw.models.TextArea):
            with open(output, "a") as file:
                file.write(widget.text + '\n\n')

    print(f'Saved description from /r/{sub} to {output}')

    # if gcs == True, upload the file to GCS 
    if (use_gcs == True):
        logger.log_struct(
        {
            "message": "Uploading file to GCS",
            "target-metadata": "sidebars",
            "severity": "INFO",
            "output": output,
            "subreddit": sub
        })
        blob_name = output[7:] # slice the "output/" at the beginning of the filename to be used as the blob name in Google Cloud
        try:
            upload_blob(output, blob_name)
        except Exception as e:
            logger.log_struct(
                {
                    "message": "Exception when Uploading to GCS",
                    "target-metadata": "sidebars",
                    "severity": "WARNING",
                    "type": str(type(e)),
                    "exception": str(e)
                })
    else:
        logger.log_struct(
        {
            "message": "Not Uploading to GCS",
            "target-metadata": "sidebars",
            "severity": "INFO",
            "subreddit": sub,
            "output": output
        })

def upload_blob(filename, destination_blob_name):
    """Uploads a file to the bucket."""

    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The contents to upload to the file
    # contents = "these are my contents"

    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client(project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(filename)

    print(
        f"{destination_blob_name} was uploaded to {bucket_name}."
    )
    logger.log_struct(
        {
            "message": "File was uploaded",
            "target-metadata": "sidebars",
            "severity": "INFO",
            "destination-name": destination_blob_name,
            "bucket-name": bucket_name
        })

def main(event_data, context):
    # We have to include event_data and context because these will be passed as arguments when invoked as a Cloud Function
    # and the runtime will freak out if the function only accepts 0 arguments... go figure
    print('** get_sidebars.py | Retrieving Sidebars **')
    logger.log_struct(
        {
            "message": "** get_sidebars.py | Retrieving Sidebars **",
            "target-metadata": "sidebars",
            "severity": "NOTICE"
        })

    subreddit_list = get_subreddits()
    for sub in subreddit_list:
        output = csv_setup(sub)
        get_sidebars(sub, output)

    print('** get_sidebars.py | DONE **')
    logger.log_struct(
        {
            "message": "** get_sidebars.py | DONE **",
            "target-metadata": "sidebars",
            "severity": "NOTICE"
        })

if __name__ == "__main__":
    main('foo', 'bar')