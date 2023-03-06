FROM python:3.11-buster

WORKDIR /subreddit-metadata-scraper

# Dependencies won't change *too* often so we install those first
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN python3 -m pip install --upgrade setuptools
RUN pip3 install -r requirements.txt

# Copy over the various files
COPY subreddits.txt subreddits.txt
COPY praw.ini praw.ini
COPY start.sh start.sh
COPY .env .env
COPY ./keys/gcs-credentials.json keys/gcs-credentials.json

# Copy all python scripts at once:
COPY ./*.py .

# Make sure we can run the start script
RUN chmod +x start.sh

# And then we start it! 
CMD [ "./start.sh" ]