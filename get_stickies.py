#! /usr/bin/python3

import praw, csv

reddit = praw.Reddit("modscraper")

def get_subreddits():
    subreddit_list = []
    with open("subreddits.txt", "r") as file:
        data = file.read()
        subreddit_list = data.split("\n")
    return subreddit_list

def csv_setup(sub):
    filename = "output/rules/" + sub + ".csv"
    with open(filename, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['priority', 'created', 'kind', 'short_name', 'description', 'violation_reason'])
    print(f'Created {filename} for /r/{sub}')
    return filename

def get_stickies(sub, output):
    # Specify which sticky to return. 1 appears at the top (default: 1).
    # https://praw.readthedocs.io/en/stable/code_overview/models/subreddit.html#praw.models.Subreddit.sticky
    counter = 1
    rules = reddit.subreddit(sub).rules
    for rule in rules:
        rule_count += 1
        row = [rule.priority, rule.created_utc, rule.kind, rule.short_name, rule.description, rule.violation_reason]
        with open(output, 'a') as file:
            writer = csv.writer(file)
            writer.writerow(row)
    print(f'Saved {rule_count} rules from /r/{sub} to {output}')

def main():
    print('** get_stickies.py | Retrieving Stikied Posts **')

    subreddit_list = get_subreddits()
    for sub in subreddit_list:
        output = csv_setup(sub)
        get_stickies(sub, output)

    print('** get_stickies.py | DONE **')

if __name__ == "__main__":
    main()