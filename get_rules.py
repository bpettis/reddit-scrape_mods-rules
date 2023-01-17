#! /usr/bin/python3

import praw

reddit = praw.Reddit("mod_scraper")

def get_subreddits():
    subreddit_list = []
    with open("subreddits.txt", "r") as file:
        data = file.read()
        subreddit_list = data.split("\n")
    return subreddit_list

def main():
    print('** get_rules.py | Retrieving Subreddit Rules **')

    subreddit_list = get_subreddits()

    print(subreddit_list)

    # subreddit = reddit.subreddit("reddit")
    # print(subreddit.title)

    print('** get_rules.py | DONE **')

if __name__ == "__main__":
    main()