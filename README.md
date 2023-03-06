# reddit-scrape_mods-rules
Retrieve information about rules, moderators, stickied posts, etc. from specified subreddits

## Dependencies

- [PRAW (Python Reddit API Wrapper)](https://github.com/praw-dev/praw)

## Config/Setup

I've created this script for my own research purposes, and so I can't necessarily guarantee that it will work in _your_ environment. These notes are provided as reference, but please don't accept my instructions as 100% "the word of god" since let's be honest I only kinda sorta know what I'm doing...

### Install packages:

`pip install -r requirements.txt`

### Reddit Authentication:

You'll need to have a Reddit account and generate Oauth2 credentials in order to authenticate to the Reddit API

Head to [https://www.reddit.com/prefs/apps/](https://www.reddit.com/prefs/apps/) to create an app

### `praw.ini`

Instead of placing Reddit credentials directly in the script, I use an external [`praw.ini` file](https://praw.readthedocs.io/en/stable/getting_started/configuration/prawini.html#praw-ini) to save configuration information. Put your credentials there, and not in the script and/or repo

### `.env`

There are some additional secrets that are stored in a `.env` file. This file should be placed at the root level of the project and contain the following information:

```
PUT THE EXAMPLE STUFF HERE YO
```

#### Google Cloud Permissions

The service account will need the following roles
- Logs Writer
- Storage Object Admin* (Read, Write, Delete)

* (if saving to Google Cloud Storage)

### Output directories

Unless you change it, the script will try to output files into a directory named `output/[TODAY'S DATE]/` with subdirectories for each script/thing to save:

```
.
└── output
    └── YYYY-MM-DD
        ├── mods
        ├── rules
        ├── sidebars
        └── stickies
```

(The entire `output` directory is excluded via `.gitignore` - please keep it this way. There really is no need to commit the subreddit metadata to the repository. This output data should be stored in your own environment)

#### Output to Google Cloud Storage
In each script, there is the option to output files to a Google Cloud Storage bucket. This is in _addition_ to the local `output` directory. But this is handy if you're running these scripts within a Docker container or some other ephemeral environment.

Set `use_gcs = True` to enable this option. With this option enabled, after a file is saved to the `output` directory it will also be uploaded to Google Cloud storage. This requires the `GCS_BUCKET_NAME` and `GCP_PROJECT` environment variables to be set. 

You'll need to have adequate permissions to access the project and bucket that you specify. If you're running in a local dev environment, you _should_ be okay as long as you've authorized with Google Cloud already. You'll also probably be okay if you're running the script in a GCE VM or in a Cloud Function.

In other environments, you'll likely need to create a credentials JSON file for a service account and place that file in your project. I have mine saved in `keys/gcs-credentials.json`

## Usage

### Subreddit List

Specify the names of the subreddits that you'd like to search for in `subreddits.txt`. Put one subreddit name per line. This list will be used within the other scripts

### Rules

Retrieve the rules for the specified subreddits, including their descriptions.

`python3 get_rules.py`

The script will create individual CSV files for each subreddit within `output/[TODAY'S DATE]/rules/`

### Sidebars

Retrieve the basic info from the sidebar, along with any TextAreas

`python3 get_sidebars.py`


### Mods

`python3 get_mods.py`

This currently doesn't work - likely due to limitations with the Reddit API (e.g. I don't think you can view this info for subs that you're not a mod of?)

## Google Cloud Logging
I've added in functionality for the scripts to write their logs to a Google Cloud Log, rather than just printing to the console. This is really handy if you're using Google Cloud, but will break things if not. 

Please be sure to set the `GCP_PROJECT` and `LOG_ID` environment variables using the `.env` file (or otherwise make sure they're in your environment)

`LOG_ID` can be any value you'd like - this will become part of the name that Cloud Logging uses to organize the logs. So giving it something descriptive like "subreddit-metadata-downloader" will probably be useful. The same log id will be used for all 4 scripts (assuming you're running them all in the same environment). 

Logs will also have a value for `target-metadata` to enable sorting by whether the script is attempting to download mods, rules, sidebars, etc.

Or if you don't want to use Google Cloud logging, you'll need to comment out any line(s) that begin with `logger.` such as:

```
logger.log_struct(
    {
        "message": "** get_stickies.py | Retrieving Stickied Posts **",
        "severity": "NOTICE"
    })
```

## Docker
I've created a simple `Dockerfile` which will build an image that includes all the scripts, dependencies, etc. When you run the container, it will run through all 4 scripts in order and then stop. This also means that if one of the scripts fails, the following ones won't run. Yeah, I know it's not great but nobody's perfect...

Build the container:

```
docker build -t subreddit-metadata .
```

Run the container:

```
docker run -d --rm --name subreddit-metadata subreddit-metadata
```

If you want to get super fancy, you can create a `cron` job to start a container on a specified schedule. Containers will be named with a timestamp from they were launched to help you know what's running. For example:

```
0 0 * * * /usr/bin/docker run --name "subreddit-metadata-$(/usr/bin/date +\%s)" --rm -d subreddit-metadata
```

will spawn a container each day at midnight to pull the most recent stuff from Reddit.


## Notes

To-dos:
- write the actual thing
- test whether the thing works