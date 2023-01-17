#! /usr/bin/python3

import praw

reddit = praw.Reddit("mod_scraper")

def main():
    print('** get_rules.py | Retrieving Subreddit Rules **')

    subreddit = reddit.subreddit("reddit")
    print(subreddit.title)

    print('** get_rules.py | DONE **')

if __name__ == "__main__":
    main()