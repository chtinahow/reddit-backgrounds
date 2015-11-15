
import requests
import json
import urllib.request
import os.path

keyfile = open('clientid.txt')
global clientid
clientid = keyfile.read().strip()
keyfile.close()

def main():
    with open('subreddits.txt') as f:
        
        for sub in [line.strip() for line in f if not line.isspace()]:
            link = 'https://www.reddit.com/r/' + sub + '.json'

            page = get_and_decode_json(link)
            
            posts = page['data']['children']

            posts = [post for post in posts if not sub in post['data']['domain']]
            
            image_links = {}

            for post in posts:
                width = str(post['data']['preview']['images'][0]['source']['width'])
                height = str(post['data']['preview']['images'][0]['source']['height'])
                url = post['data']['url']
                print(url)

                if url.endswith('.jpg') or url.endswith('.png'):
                    print('simple image')

                    image_links[post['data']['id']] = url

                elif 'imgur' in url and 'gallery' in url:
                    print('imgur gallery')

                    imgur = get_and_decode_json(url + '.json')
                    data = imgur['data']

                    if 'album_images' in data:
                        print('multiple images in album')

                        for image in data['album_images']['images']:
                            hsh = image['hash']
                            image_links[hsh] = 'https://imgur.com/' + hsh

                    else:
                        print('one image in album')

                        hsh = data['image']['hash']
                        #api = get_and_decode_json('https://api.imgur.com/3/album/' + str(id) + '/images')
                        #print(api)
                        image_links['hsh'] = 'https://imgur.com/' + hsh + '.jpg'

                print()

            # Fetch the images
            for id, link in image_links.items():
                filename = 'images/' + id + '.jpg'
                if not os.path.isfile(filename):
                    print('downloading ' + link + '...')
                    download_image(link, filename)
                else:
                    print(link + ' already downloaded, skipping...')

def get_and_decode_json(url):
    global clientid
    headers = {}
    headers['User-Agent'] = 'this is my fancy user agent'
    headers['Authorization'] = 'Client-ID ' + clientid
    request = requests.get(url, headers=headers)
    return json.loads(request.text)

def download_image(url, dest):
    #f = open('images/' + str(i) + '.jpg', 'wb')
    f = open(dest, 'wb')
    f.write(requests.get(url).content)
    f.close()

if __name__ == '__main__':
    main()
                