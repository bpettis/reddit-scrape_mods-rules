#! /usr/bin/python3

import praw

reddit = praw.Reddit("modscraper")

def get_subreddits():
    subreddit_list = []
    with open("subreddits.txt", "r") as file:
        data = file.read()
        subreddit_list = data.split("\n")
    return subreddit_list

def csv_setup(sub):
    filename = "output/sidebars/" + sub + ".txt"
    with open(filename, 'w') as file:
        file.write('Sidebar for /r/' + sub + '\n\n')
    print(f'Created {filename} for /r/{sub}')
    return filename

def get_sidebars(sub, output):
    id_card = reddit.subreddit(sub).widgets.id_card
    with open(output, "a") as file:
        file.write(str(id_card.subscribersCount) + ' ' + id_card.subscribersText + '\n\n')
        file.write(id_card.description + '\n\n')
    widgets = reddit.subreddit(sub).widgets.sidebar
    for widget in widgets:
        if isinstance(widget, praw.models.TextArea):
            with open(output, "a") as file:
                file.write(widget.text + '\n\n')

    print(f'Saved description from /r/{sub} to {output}')

def main():
    print('** get_sidebars.py | Retrieving Subreddit Sidebars **')

    subreddit_list = get_subreddits()
    for sub in subreddit_list:
        output = csv_setup(sub)
        get_sidebars(sub, output)

    print('** get_sidebars.py | DONE **')

if __name__ == "__main__":
    main()