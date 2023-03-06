#! /usr/bin/python3

import praw, csv, os
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
    Path("output/" + today + "/rules").mkdir(parents=True, exist_ok=True)
    filename = "output/" + today + "/rules/" + sub + ".csv"
    with open(filename, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['priority', 'created', 'kind', 'short_name', 'description', 'violation_reason'])
    print(f'Created {filename} for /r/{sub}')
    return filename

def get_rules(sub, output):
    rules = reddit.subreddit(sub).rules
    rule_count = 0
    for rule in rules:
        rule_count += 1
        row = [rule.priority, rule.created_utc, rule.kind, rule.short_name, rule.description, rule.violation_reason]
        with open(output, 'a') as file:
            writer = csv.writer(file)
            writer.writerow(row)
    print(f'Saved {rule_count} rules from /r/{sub} to {output}')

    # if > 0 rules saved AND if gcs == True, upload the file to GCS 
    if (rule_count > 0) and (use_gcs == True):
        logger.log_struct(
        {
            "message": "Uploading file to GCS",
            "severity": "INFO",
            "count": str(rule_count),
            "output": output,
            "subreddit": sub,
            "target-metadata": "rules"
        })
        blob_name = output[7:] # slice the "output/" at the beginning of the filename to be used as the blob name in Google Cloud
        try:
            upload_blob(output, blob_name)
        except Exception as e:
            logger.log_struct(
                {
                    "message": "Exception when Uploading to GCS",
                    "severity": "WARNING",
                    "target-metadata": "rules",
                    "type": str(type(e)),
                    "exception": str(e)
                })
    else:
        logger.log_struct(
        {
            "message": "Not Uploading to GCS",
            "severity": "INFO",
            "subreddit": sub,
            "target-metadata": "rules",
            "count": str(rule_count),
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
            "target-metadata": "rules",
            "severity": "INFO",
            "destination-name": destination_blob_name,
            "bucket-name": bucket_name
        })

def main(event_data, context):
    # We have to include event_data and context because these will be passed as arguments when invoked as a Cloud Function
    # and the runtime will freak out if the function only accepts 0 arguments... go figure
    print('** get_rules.py | Retrieving Subreddit Rules **')
    logger.log_struct(
        {
            "message": "** get_rules.py | Retrieving Subreddit Rules **",
            "severity": "NOTICE",
            "target-metadata": "rules"
        })

    subreddit_list = get_subreddits()
    for sub in subreddit_list:
        output = csv_setup(sub)
        get_rules(sub, output)

    print('** get_rules.py | DONE **')
    logger.log_struct(
        {
            "message": "** get_rules.py | DONE **",
            "target-metadata": "rules",
            "severity": "NOTICE"
        })

if __name__ == "__main__":
    main('foo', 'bar')