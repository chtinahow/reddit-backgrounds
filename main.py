
import requests
import json
import urllib.request

with open('subreddits.txt') as f:
    
    for sub in [line.strip() for line in f if not line.isspace()]:
        link = 'https://www.reddit.com/r/' + sub + '.json'

        headers = {'User-Agent': 'this is a user agent'}
        request = requests.get(link, headers=headers)

        page = json.loads(request.text)
        
        posts = page['data']['children']

        posts = [post for post in posts if not sub in post['data']['domain']]
        
        i = 0
        for post in posts:
            width = str(post['data']['preview']['images'][0]['source']['width'])
            height = str(post['data']['preview']['images'][0]['source']['height'])
            url = post['data']['url']

            print(url)
            print(str(i) + '.jpg')
            print()

            f = open('images/' + str(i) + '.jpg', 'wb')
            f.write(requests.get(url).content)
            f.close()

            i += 1

            