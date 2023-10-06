import requests
import urllib.parse as parser
import re
import logging

LOG = logging.getLogger(__name__)

def paraphrase(data:str,lang:str,mode:str)->str:
    """
    ``lang:`` fr / en
    """

    url = "https://www.paraphraser.io/frontend/rewriteArticleBeta"
    
    session = requests.Session()
    session.get("https://www.paraphraser.io/")
    headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://www.paraphraser.io" ,
    "Referer": "https://www.paraphraser.io/"
    }

    body = "data="+parser.quote_plus(data)+'+&mode='+mode+'&lang='+lang+'&captcha='

    LOG.info(f"post request body: {body}")
    response = session.post(url,  headers=headers, data=body)
    LOG.info(f"POST request returned with {response}")
    LOG.info(f"response body: {response.text}")

    response =  response.json()
    if mode == "3" or (mode =="4" and lang =="fr"):
        paraphrasedText = response["result"]["paraphrase"]
        regex = "<span class='sw'>(.*?)</span>"
        result = re.findall(regex,paraphrasedText)
        ret = ' '.join(result)
    elif mode == "5" or (mode == "4" and lang == "en"):
        paraphrasedText = response["result"]["final_result"]
        ret = paraphrasedText

    LOG.info(f"paraphraser returned with: {ret}")
    return ret
print(paraphrase("hello world paraphrase this please hi there","en","5"))