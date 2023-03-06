#! /usr/bin/python3

import praw, prawcore, csv, os
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
    Path("output/" + today + "/stickies").mkdir(parents=True, exist_ok=True)
    filename = "output/" + today + "/stickies/" + sub + ".csv"
    with open(filename, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'created', 'author', 'title', 'url', 'text'])
    print(f'Created {filename} for /r/{sub}')
    return filename

def get_stickies(sub, output):
    # Specify which sticky to return. 1 appears at the top (default: 1).
    # https://praw.readthedocs.io/en/stable/code_overview/models/subreddit.html#praw.models.Subreddit.sticky
    counter = 1
    lastid = ''
    while counter > 0:
        # Depreciation Notice
        # DeprecationWarning: Positional arguments for 'Subreddit.sticky' will no longer be supported in PRAW 8
        # Call this function with 'number' as a keyword argument.
        print(f'Sticky #{str(counter)}')
        try:
            sticky = reddit.subreddit(sub).sticky(counter)

            if (sticky.id == lastid):
                break
            else:
                lastid = sticky.id

            row = [sticky.id, sticky.created_utc, sticky.author.name, sticky.title, sticky.url, sticky.selftext]
            with open(output, 'a') as file:
                writer = csv.writer(file)
                writer.writerow(row)
            counter += 1
        except prawcore.exceptions.NotFound:
            print('Not found')
            logger.log_struct(
                {
                    "message": "Not Found (prawcore.exceptions.NotFound)",
                    "severity": "WARNING",
                    "subreddit": sub,
                    "counter": str(counter),
                    "output": output
                })
            break
        except Exception as e:
            print(f'Got some other error: {type(e).__name__}')
            break

    print(f'Saved {str(counter - 1)} stickies from /r/{sub} to {output}')
    if (counter > 1) and (use_gcs == True):
        logger.log_struct(
        {
            "message": "Uploading file to GCS",
            "severity": "INFO",
            "count": str(counter - 1),
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
                    "severity": "WARNING",
                    "type": str(type(e)),
                    "exception": str(e)
                })
    else:
        logger.log_struct(
        {
            "message": "Not Uploading to GCS",
            "severity": "INFO",
            "subreddit": sub,
            "count": str(counter - 1),
            "output": output
        })
    # if > 0 stickies saved AND if gcs == True, upload the file to GCS 

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
            "severity": "INFO",
            "destination-name": destination_blob_name,
            "bucket-name": bucket_name
        })

def main(event_data, context):
    # We have to include event_data and context because these will be passed as arguments when invoked as a Cloud Function
    # and the runtime will freak out if the function only accepts 0 arguments... go figure
    print('** get_stickies.py | Retrieving Stickied Posts **')
    logger.log_struct(
        {
            "message": "** get_stickies.py | Retrieving Stickied Posts **",
            "severity": "NOTICE"
        })

    subreddit_list = get_subreddits()
    for sub in subreddit_list:
        output = csv_setup(sub)
        get_stickies(sub, output)

    print('** get_stickies.py | DONE **')
    logger.log_struct(
        {
            "message": "** get_stickies.py | DONE **",
            "severity": "NOTICE"
        })

if __name__ == "__main__":

    main('foo', 'bar') # see note in main() for why we have these filler variables that aren't actually doing anything...