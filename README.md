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

### praw.ini

Instead of placing Reddit credentials directly in the script, I use an external [`praw.ini` file](https://praw.readthedocs.io/en/stable/getting_started/configuration/prawini.html#praw-ini) to save configuration information. Put your credentials there, and not in the script and/or repo

### Output directories

Unless you change it, the script will try to output files into a directory named `output` with subdirectories for each script/thing to save:

```
.
└── output
    ├── mods
    ├── rules
    ├── sidebars
    └── stickies
```

Please be sure to create these directories if they do not already exist (the entire `output` directory is excluded via `.gitignore`)


## Usage

### Subreddit List

Specify the names of the subreddits that you'd like to search for in `subreddits.txt`. Put one subreddit name per line. This list will be used within the other scripts

### Rules

Retrieve the rules for the specified subreddits, including their descriptions.

`python3 get_rules.py`

The script will create individual CSV files for each subreddit within `output/rules/`

### Sidebars

Retrieve the basic info from the sidebar, along with any TextAreas

`python3 get_sidebars.py`


### Mods

`python3 get_mods.py`

This currently doesn't work - likely due to limitations with the Reddit API (e.g. I don't think you can view this info for subs that you're not a mod of?)

## Notes

To-dos:
- write the actual thing
- test whether the thing works