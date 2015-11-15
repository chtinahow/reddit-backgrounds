
import requests
import json
import urllib.request
import os.path
import sys

keyfile = open('clientid.txt')
global clientid
clientid = keyfile.read().strip()
keyfile.close()

def main():
    with open('subreddits.txt') as f:
        
        for sub in [line.strip() for line in f if not line.isspace()]:
            link = 'https://www.reddit.com/r/' + sub + '/.json'

            for i in range(0, 5):
                print('link: ' + link)
                after = crawl_page(link, sub)
                if after == None:
                    break
                link = 'https://www.reddit.com/r/' + sub + '/.json?count=25&after=t3_' + after

def crawl_page(link, sub):

    page = get_and_decode_json(link)
    
    posts = page['data']['children']

    posts = [post for post in posts if not sub in post['data']['domain']]
    
    image_links = {}
    after = None

    for post in posts:
        print(post['data']['url'])
        if 'preview' not in post['data']:
            # No size, no save
            continue

        width = str(post['data']['preview']['images'][0]['source']['width'])
        height = str(post['data']['preview']['images'][0]['source']['height'])
        url = post['data']['url']
        #print(url)
        after = post['data']['id']

        if not image_is_right_size(width, height):
            continue

        if url.endswith('.jpg') or url.endswith('.png'):
            #print('simple image')

            image_links[post['data']['id']] = url

        elif 'imgur' in url and 'gallery' in url:
            #print('imgur gallery')

            imgur = get_and_decode_json(url + '.json')
            data = imgur['data']

            if 'album_images' in data:
                #print('multiple images in album')

                for image in data['album_images']['images']:
                    hsh = image['hash']
                    image_links[hsh] = 'https://imgur.com/' + hsh

            else:
                #print('one image in album')

                hsh = data['image']['hash']
                #api = get_and_decode_json('https://api.imgur.com/3/album/' + str(id) + '/images')
                #print(api)
                image_links['hsh'] = 'https://imgur.com/' + hsh + '.jpg'

        #print()

    # Fetch the images
    for id, link in image_links.items():
        filename = 'images/' + id + '.jpg'
        if not os.path.isfile(filename):
            print('downloading ' + link + '...')
            timeout(download_image, (link, filename), timeout_duration=10)
        else:
            print(link + ' already downloaded, skipping...')

    return after

def get_and_decode_json(url):
    global clientid
    headers = {}
    headers['User-Agent'] = 'this is my fancy user agent'
    headers['Authorization'] = 'Client-ID ' + clientid
    request = requests.get(url, headers=headers, timeout=2)
    return json.loads(request.text)

def image_is_right_size(width, height):
    return int(width) >= 1920 and int(height) >= 1080 \
        and int(width) > int(height)

def download_image(url, dest):
    #f = open('images/' + str(i) + '.jpg', 'wb')
    f = open(dest, 'wb')
    f.write(requests.get(url).content)
    f.close()

def timeout(func, args=(), kwargs={}, timeout_duration=1, default=None):
    import signal

    class TimeoutError(Exception):
        pass

    def handler(signum, frame):
        raise TimeoutError()

    # set the timeout handler
    signal.signal(signal.SIGALRM, handler) 
    signal.alarm(timeout_duration)
    try:
        result = func(*args, **kwargs)
    except TimeoutError as exc:
        result = default
    finally:
        signal.alarm(0)

    return result

if __name__ == '__main__':
    main()
                