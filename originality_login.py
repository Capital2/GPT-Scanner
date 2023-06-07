
from fake_useragent import UserAgent
import requests

client = requests.session()
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

data = {"email":"u15cfhvtf6qqn4f6dxyvble7@getsingspiel.com","password":"heyyeyeyyha551ABqsd","captcha":"null"}

r = client.post(url="https://core.originality.ai/api/user/login", json=data)

token = r.json()["auth_data"]["access_token"]
client.headers.update({
    "Authorization": f"Bearer {token}"
})
r = client.post("https://core.originality.ai/api/user/apiKeys/create")

print(r.text)
