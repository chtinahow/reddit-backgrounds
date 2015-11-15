
import requests

with open('subreddits.txt') as f:
    
    for sub in [line.strip() for line in f if not line.isspace()]:
    	print(sub + '1')

    	link = 'https://reddit.com/' + sub + '/'

    	page = reques
    		
