from uuid import uuid4
from fake_useragent import UserAgent
import cloudscraper

scraper = cloudscraper.create_scraper()

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
    "document": "Hannibal of Carthage was a highly respected military general and statesman who commanded the forces of Carthage in their fight against the Roman Republic during the Second Punic War [8]. He was born into a period of great tension in the Mediterranean Basin, with Carthaginians seeking revenge against Rome after their defeat in the First Punic War. Hannibal is widely regarded as one of the greatest military commanders in history, known for his ability to determine his and his opponent's strengths and weaknesses and plan battles accordingly. He was also distinguished for his well-planned strategies and ability to conquer and ally with several Italian cities. Hannibal won several victories against Rome, including at the battles of Trebia, Lake Trasimene, and Cannae, inflicting heavy losses on the Romans. However, despite his best efforts, he was unable to win a decisive victory and was eventually forced to flee into exile. Hannibal is considered one of the greatest military tacticians and generals of antiquity, alongside other greats such as Julius Caesar and Alexander the Great.",
}
r = scraper.post(url="https://api.gptzero.me/v2/predict/text",headers=headers, json=data)

print(r.text)