from fake_useragent import UserAgent
import requests
import re

url = "https://u29261027.ct.sendgrid.net/ls/click?upn=hXD8YzvTkcoYbVfxPXa1F1kazsh9olBcbjAkpH1t6dEcENUdVLltRBZfPPaPW9837bFejPO7VB6esC7W-2FWtlX1oaJS3F-2FTPxcIV-2F14jBmgKZAcOy1QhheLV88V1Hfq9HEZZ__7R2tjMqH85LCkgPyBsbAUTv5lM3eama0p3qMazc2fwSmSl63nrbdOsSMEjU-2FjMbrm-2FOTYYOB-2BQoQ2ZFF6QMaUJglArQCnojMcRAftpnODAJ0t2uQ9pfYUK3ZC6h2MW9YoX53WFsuY1PEN1yPv5g4fXTVaCK8SQtnwN9dGF2X4CIjCiazJpdT0go-2FttgoqB-2Ftl6Na9DYfJIGSJRyldEpDjp8digBi7xcrlbM0-2BkqN-2FDM-3D"

scraper = requests.session()
headers = {
            'authority': 'core.originality.ai',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en,fr-FR;q=0.9,fr;q=0.8,es-ES;q=0.7,es;q=0.6,en-US;q=0.5,am;q=0.4,de;q=0.3',
            'cache-control': 'no-cache',
            'referer': 'https://app.originality.ai/',
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': UserAgent().random,
}

scraper.headers = headers

# the url return 302
# so we get the new  location url that has token
r = scraper.get(url)

verifurl = "https://core.originality.ai/api/user/email/verify"

print(r.url)
token = re.search(r'(?<=\?token=).*', r.url)
print(f"{verifurl}?token={token.group(0)}")

r = scraper.get(f"{verifurl}?token={token.group(0)}")
print(r.text)