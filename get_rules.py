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
    print(f'Created {filename} for {sub}')
    return filename

def get_rules(sub, output):
    rules = reddit.subreddit(sub).rules
    for rule in rules:
        # print(rule)
        # print(rule.created_utc)
        # print(rule.kind)
        # print(rule.description)
        row = [rule.priority, rule.created_utc, rule.kind, rule.short_name, rule.description, rule.violation_reason]
        with open(output, 'a') as file:
            writer = csv.writer(file)
            writer.writerow(row)

def main():
    print('** get_rules.py | Retrieving Subreddit Rules **')

    subreddit_list = get_subreddits()
    for sub in subreddit_list:
        output = csv_setup(sub)
        get_rules(sub, output)

    print('** get_rules.py | DONE **')

if __name__ == "__main__":
    main()