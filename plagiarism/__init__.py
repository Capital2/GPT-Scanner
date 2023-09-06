import requests
import urllib.parse as parser
def plagiarismChecker(data:str)->list[dict]:
    url = "https://seomagnifier.com/online-plagiarism-checker/check"

    headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    }
    data = data.replace(".","_sysbreak_[--atozbreak--]")
    
    body = "queries="+parser.quote_plus(data)+"&SecureToken=ggggggg"
    response = requests.post(url,  headers=headers, data=body)
    response = response.json()['details']
    list_of_queries = []
    
    for item in response:
        if item["unique"] == False:
            query = {"text":item["query"],"link":item["webs"][0]["url"]}
        else:
            query = {"text":item["query"],"link":"None"}
        list_of_queries.append(query)
    return list_of_queries