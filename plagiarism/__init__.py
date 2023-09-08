# import requests
# import urllib.parse as parser
# from googlesearch import search
# from difflib import SequenceMatcher
# import logging

# LOG = logging.getLogger(__name__)

# def plagiarismChecker(data:str)->list[dict]:
#     url = "https://seomagnifier.com/online-plagiarism-checker/check"
#     ultraSuperSecureSecretToken="ggggggg"
#     headers = {
#     "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0",
#     "Accept": "application/json, text/javascript, */*; q=0.01",
#     "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
#     "X-Requested-With": "XMLHttpRequest",
#     }
#     data = data.replace(".","_sysbreak_[--atozbreak--]")
    
#     body = "queries="+parser.quote_plus(data)+f"&SecureToken={ultraSuperSecureSecretToken}"
#     LOG.debug(f"post request body: {body}")
#     response = requests.post(url,  headers=headers, data=body)
#     LOG.info(f"POST request returned with {response}")
#     LOG.debug(f"response body: {response.text}")
#     response = response.json()['details']
#     list_of_queries = []
    
#     for item in response:
#         if item["unique"] == False:
#             query = {"text":item["query"],"link":item["webs"][0]["url"]}
#         else:
#             query = {"text":item["query"],"link":"None"}
#         list_of_queries.append(query)
#     LOG.debug(f"plag checker returned with: {list_of_queries}")

#     return list_of_queries

import requests
import json
def turnitinPlagaiarsimChecker(data:str,lang:str)->dict:
    """
    credits to:    https://github.com/SegYT/turnitinFree

    Return
    -----------------
    ``turnitin_index:`` overall plagiarism percentage \n
    ``matches``: list of dict that contain possible website and their relative percentage 

    
    """
    burp0_url = "https://papersowl.com:443/plagiarism-checker-send-data"

    burp0_cookies = {"PHPSESSID": "qjc72e3vvacbtn4jd1af1k5qn1", "first_interaction_user": "%7B%22referrer%22%3A%22https%3A%5C%2F%5C%2Fwww.google.com%5C%2F%22%2C%22internal_url%22%3A%22%5C%2Ffree-plagiarism-checker%22%2C%22utm_source%22%3Anull%2C%22utm_medium%22%3Anull%2C%22utm_campaign%22%3Anull%2C%22utm_content%22%3Anull%2C%22utm_term%22%3Anull%2C%22gclid%22%3Anull%2C%22msclkid%22%3Anull%2C%22adgroupid%22%3Anull%2C%22targetid%22%3Anull%2C%22appsflyer_id%22%3Anull%2C%22appsflyer_cuid%22%3Anull%2C%22cta_btn%22%3Anull%7D", "first_interaction_order": "%7B%22referrer%22%3A%22https%3A%5C%2F%5C%2Fwww.google.com%5C%2F%22%2C%22internal_url%22%3A%22%5C%2Ffree-plagiarism-checker%22%2C%22utm_source%22%3Anull%2C%22utm_medium%22%3Anull%2C%22utm_campaign%22%3Anull%2C%22utm_content%22%3Anull%2C%22utm_term%22%3Anull%2C%22gclid%22%3Anull%2C%22msclkid%22%3Anull%2C%22adgroupid%22%3Anull%2C%22targetid%22%3Anull%2C%22appsflyer_id%22%3Anull%2C%22appsflyer_cuid%22%3Anull%2C%22cta_btn%22%3Anull%7D", "affiliate_user": "a%3A3%3A%7Bs%3A9%3A%22affiliate%22%3Bs%3A9%3A%22papersowl%22%3Bs%3A6%3A%22medium%22%3Bs%3A9%3A%22papersowl%22%3Bs%3A8%3A%22campaign%22%3Bs%3A9%3A%22papersowl%22%3B%7D", "sbjs_migrations": "1418474375998%3D1", "sbjs_current_add": "fd%3D2022-05-24%2019%3A01%3A22%7C%7C%7Cep%3Dhttps%3A%2F%2Fpapersowl.com%2Ffree-plagiarism-checker%7C%7C%7Crf%3Dhttps%3A%2F%2Fwww.google.com%2F", "sbjs_first_add": "fd%3D2022-05-24%2019%3A01%3A22%7C%7C%7Cep%3Dhttps%3A%2F%2Fpapersowl.com%2Ffree-plagiarism-checker%7C%7C%7Crf%3Dhttps%3A%2F%2Fwww.google.com%2F", "sbjs_current": "typ%3Dorganic%7C%7C%7Csrc%3Dgoogle%7C%7C%7Cmdm%3Dorganic%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29", "sbjs_first": "typ%3Dorganic%7C%7C%7Csrc%3Dgoogle%7C%7C%7Cmdm%3Dorganic%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29", "sbjs_udata": "vst%3D1%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Windows%20NT%206.3%3B%20Win64%3B%20x64%3B%20rv%3A100.0%29%20Gecko%2F20100101%20Firefox%2F100.0", "sbjs_session": "pgs%3D1%7C%7C%7Ccpg%3Dhttps%3A%2F%2Fpapersowl.com%2Ffree-plagiarism-checker", "_ga_788D7MTZB4": "GS1.1.1653411683.1.0.1653411683.0", "_ga": "GA1.1.1828699233.1653411683", "trustedsite_visit": "1", "trustedsite_tm_float_seen": "1", "AppleBannercookie_hide_header_banner": "1", "COOKIE_PLAGIARISM_CHECKER_TERMS": "1", "plagiarism_checker_progress_state": "1"}

    burp0_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0", "Accept": "*/*", "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3", "Accept-Encoding": "gzip, deflate", "Referer": "https://papersowl.com/free-plagiarism-checker", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Requested-With": "XMLHttpRequest", "Origin": "https://papersowl.com", "Dnt": "1", "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "no-cors", "Sec-Fetch-Site": "same-origin", "Pragma": "no-cache", "Cache-Control": "no-cache", "Te": "trailers", "Connection": "close"}

    burp0_data = {"is_free": "false", "plagchecker_locale": lang, "product_paper_type": "1", "title": '', "text": data}

    r = requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=burp0_data)

    result = json.loads(r.text)

    #result contains word_count:int, percent:float, matches:list[dict]
    #matches contains url:str ,percent:float ,highlight:list[list]
    
    return {
        "turnitin_index": str(100 - float(result["percent"])),
        "match": result["matches"][0] if len(result["matches"])>0 else None #getting only the first match which is the highest match percentage among all links
        } 
