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

def main():
    print('** get_rules.py | Retrieving Subreddit Rules **')

    subreddit_list = get_subreddits()
    for sub in subreddit_list:
        output = csv_setup(sub)
        get_rules(sub, output)

    print('** get_rules.py | DONE **')

if __name__ == "__main__":
    main()