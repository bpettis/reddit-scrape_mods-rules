#! /usr/bin/python3

import praw
from datetime import datetime
from pathlib import Path

reddit = praw.Reddit("modscraper")

def get_subreddits():
    subreddit_list = []
    with open("subreddits.txt", "r") as file:
        data = file.read()
        subreddit_list = data.split("\n")
    return subreddit_list

def csv_setup(sub):
    today = datetime.today().strftime('%Y-%m-%d')
    Path("output/" + today + "/mods").mkdir(parents=True, exist_ok=True)
    filename = "output/" + today + "/mods/" + sub + ".txt"
    with open(filename, 'w') as file:
        file.write('Moderators for /r/' + sub + '\n\n')
    print(f'Created {filename} for /r/{sub}')
    return filename

def get_mods(sub, output):
    count = reddit.subreddit(sub).widgets.moderators_widget.totalMods
    mods = reddit.subreddit(sub).widgets.moderators_widget.mods
    with open(output, 'a') as file:
        file.write(str(count) + ' mods found\n\n')
        for mod in mods:
            print(mod.name)

    print(f'Saved mods from /r/{sub} to {output}')

def main():
    print('** get_mods.py | Retrieving Subreddit Moderators **')

    subreddit_list = get_subreddits()
    for sub in subreddit_list:
        output = csv_setup(sub)
        get_mods(sub, output)

    print('** get_mods.py | DONE **')

if __name__ == "__main__":
    main()