import requests

"""
    requires an account 5addem pymailtm
    every account has 50 credits if mail is verified
"""

data = {
  "title": "optional title",
  "content": "My life wasn't very exciting but I loved my job as a nurse. Being able to take care of people who need help  has always been something I enjoyed doing. I sometimes believe it's because I've been taking care of people my whole life. When I was around 13, I had to take care of both my mother and little sister. My father left after my little sister was born, I never knew him well and my mother had been diagnosed with lung cancer. It wasn't easy for me but I got used to it. My mother passed away when I was 18 and was left alone with my sister to take care of. "
}

headers = {
    'X-OAI-API-KEY': '0ken5pwivyfs214ah78gc6uzqtoxmrb9'
}

r = requests.post("https://api.originality.ai/api/v1/scan/ai-plag", headers=headers, json=data)

print(r.text)