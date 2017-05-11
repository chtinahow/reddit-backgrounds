
import requests
import json
import urllib.request
import os.path
import sys
import urllib
import json


global clientid

def main():
    keyfile = open('config.json')
    data = json.loads(keyfile.read())
    if "clientid" not in data:
        print("warning: clientid field isn't in json")
    else:
        global clientid
        clientid = data["clientid"]
        print("client id: %s" % clientid)

    with open('subreddits.txt') as f:
        
        for sub in [line.strip() for line in f if not line.isspace()]:
            if 'top' in sys.argv:
                top = 'top/'
                url_params = {'sort': 'top', 't': 'all'}
            else:
                top = ''
                url_params = {}

            link = 'https://www.reddit.com/r/' + sub + '/' + top + '.json' + get_params(url_params)

            after = None

            for i in range(0, 10):
                print('link: ' + link)
                after = crawl_page(link, sub)
                if after == None:
                    break
                url_params['count'] = 25
                url_params['after'] = 't3_' + after
                link = 'https://www.reddit.com/r/' + sub + '/' + top + '.json' + get_params(url_params)

def crawl_page(link, sub):

    page = get_and_decode_json(link)

    #print(link)
    
    posts = page['data']['children']

    posts = [post for post in posts if not sub in post['data']['domain']]
    
    image_links = {}
    after = None

    for post in posts:
        #print(post['data']['url'])
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

            try:
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
            except Exception:
                pass

        #print()

    # Fetch the images
    for id, link in image_links.items():
        filename = 'images/' + id + '.jpg'
        if not os.path.isfile(filename):
            print('\tdownloading ' + link + '...')
            try:
                timeout(download_image, (link, filename), timeout_duration=10)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(e)
        else:
            print('\tskipping ' + link + ', already downloaded...')

    return after

def get_and_decode_json(url):
    global clientid
    headers = {}
    headers['User-Agent'] = 'this is my fancy user agent'
    headers['Authorization'] = 'Client-ID ' + clientid
    request = requests.get(url, headers=headers)
    return json.loads(request.text)

def image_is_right_size(width, height):
    return int(width) >= 1920 and int(height) >= 1080 \
        and int(width) > int(height)

def download_image(url, dest):
    #f = open('images/' + str(i) + '.jpg', 'wb')
    #f = open(dest, 'wb')
    d = requests.get(url, params = None, allow_redirects = False)
    if d.status_code == 200:
        f = open(dest, 'wb')
        f.write(d.content)
        f.close()

def get_params(d):
    string = ''
    i = 0
    for param in d:
        start = '?' if i == 0 else '&'
        string += start + str(param) + '=' + str(d[param])
        i += 1

    return string

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
                
