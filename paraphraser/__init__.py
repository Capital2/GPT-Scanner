import requests
import urllib.parse as parser
import re

def paraphrase(data:str,lang:str)->str:
    """
    ``lang:`` fr / en
    """

    url = "https://www.paraphraser.io/frontend/rewriteArticleBeta"

    headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://www.paraphraser.io" ,
    "Referer": "https://www.paraphraser.io/fr/outil-de-paraphrase"
    }

    body = "data="+parser.quote_plus(data)+'+&mode=1&lang='+lang

    response = requests.post(url,  headers=headers, data=body)
    response =  response.json()
    paraphrasedText = response["result"]["paraphrase"]
    
    regex = "<span class='sw'>(.*?)</span>"
    result = re.findall(regex,paraphrasedText)

    return ' '.join(result)
