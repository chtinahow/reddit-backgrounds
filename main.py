
import requests
import json

with open('subreddits.txt') as f:
    
    for sub in [line.strip() for line in f if not line.isspace()]:
        link = 'https://www.reddit.com/r/' + sub + '.json'
        print(link)

        headers = {'User-Agent': 'this is a user agent'}
        request = requests.get(link, headers=headers)

        page = json.loads(request.text)
        for key in page.keys():
            print(key)

        print(page['kind'])
        