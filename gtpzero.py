from fake_useragent import UserAgent
import requests
# import cloudscraper

"""
IP ban after 7 requests each hour
"""


# scraper = cloudscraper.create_scraper()

scraper = requests.session()
headers = {
            'authority': 'https://gptzero.me/',
            'accept': 'text/event-stream',
            'accept-language': 'en,fr-FR;q=0.9,fr;q=0.8,es-ES;q=0.7,es;q=0.6,en-US;q=0.5,am;q=0.4,de;q=0.3',
            'cache-control': 'no-cache',
            'referer': 'https://gptzero.me/',
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': UserAgent().random,
}

data = {
    "document": "My life is quite boring to be honest. Every morning I wake up and do the same thing over again-turn off my beeping alarm clock, force myself out of bed, take a quick shower, change into my scrubs and rush out the house to the hospital. I Work there for what feels like forever, and come back home to sleep and redo everything over again. My life wasn't very exciting but I loved my job as a nurse. Being able to take care of people who need help  has always been something I enjoyed doing. I sometimes believe it's because I've been taking care of people my whole life. When I was around 13, I had to take care of both my mother and little sister. My father left after my little sister was born, I never knew him well and my mother had been diagnosed with lung cancer. It wasn't easy for me but I got used to it. My mother passed away when I was 18 and was left alone with my sister to take care of. ",
}
r = scraper.post(url="https://api.gptzero.me/v2/predict/text",headers=headers, json=data)

print(r.text)