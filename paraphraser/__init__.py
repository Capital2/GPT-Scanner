import requests
import urllib.parse as parser
import re
import logging

LOG = logging.getLogger(__name__)

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

    LOG.info(f"post request body: {body}")
    response = requests.post(url,  headers=headers, data=body)
    LOG.info(f"POST request returned with {response}")
    LOG.info(f"response body: {response.text}")

    response =  response.json()
    paraphrasedText = response["result"]["paraphrase"]
    
    regex = "<span class='sw'>(.*?)</span>"
    result = re.findall(regex,paraphrasedText)
    ret = ' '.join(result)

    LOG.info(f"paraphraser returned with: {ret}")
    return ret
