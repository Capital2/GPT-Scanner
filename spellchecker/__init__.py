import logging
from fake_useragent import UserAgent

import requests
from time import sleep
from langdetect import DetectorFactory, detect
if __name__ == '__main__':
    import json

LOG = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%d/%b/%Y %H:%M:%S")

SPELL_URL="https://orthographe.reverso.net/api/v1/Spelling/"


def reverso_spellchecker(content: str):

    s = requests.Session()
    s.headers = {
            'authority': 'orthographe.reverso.net',
            'accept': 'text/json',
            'Accept-Encoding': "gzip, deflate, b",
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'Content-Type': "application/*+json",
            "Content-Length": "611",
            'origin': "https://www.reverso.net",
            'referer': 'https://www.reverso.net/',
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': 'Windows',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': UserAgent().random,
        }
    
    # enforce consistent detection results
    DetectorFactory.seed = 0
    lang = detect(content)

    if lang == 'en':
        lang = 'eng'
        LOG.info(f"detected language: english")
    elif lang == 'fr':
        lang = 'fra'
        LOG.info(f"detected language: français")
    else:
        LOG.warning(f"detected language is {lang} with input text :{content}\n defaulting to français")
        lang = 'fra'

    reqbody = {
        "englishDialect":"indifferent", # deletable
        "autoReplace":True,
        "getCorrectionDetails":True,
        "interfaceLanguage":"en", # deletable
        "locale":"", # deletable
        "language":lang,
        "text": content,
        "originalText":"",
        "spellingFeedbackOptions":
            {"insertFeedback":True,"userLoggedOn":True},

        "isHtml":False,
        "IsUserPremium":True
        }
    retries = 3
    for i in range(retries):
        r = s.post(SPELL_URL, json=reqbody)
        if r.ok:
            return r.json()
        elif r.status_code == 429:
            # too many requests
            sleep(i+1)
        else:
            LOG.error(f"[{r.status_code}] reverso returned:\n{r.text}")
    return None


if __name__ == '__main__':
    content = "on ne peut pas le faire, c'est trop difficiles d'avoir ce type de trucs ici, il faut etre un peu vigilan"

    for i in range(1):
        sleep(0.5)
        r = reverso_spellchecker(content)
        print(json.dumps(r.json(), indent=4))
        # print(f"{i}: {r.text if not r.ok else 'true'}")
        # if not r.ok:
        #     print(r.headers)


# return example
# {
#     "id": "06741442-6baa-4379-ab90-18a6df01a1a0",
#     "language": "fra",
#     "text": "on ne peut pas le faire, c'est trop difficile d'avoir ce type de trucs ici, il faut \u00eatre un peu vigilant",
#     "engine": "NeuroSpell",
#     "truncated": false,
#     "timeTaken": 514,
#     "corrections": [
#         {
#             "group": "AutoCorrected",
#             "type": "Spelling",
#             "shortDescription": "Spelling Mistake",
#             "longDescription": "Le mot pluriel \u00ab\u00a0difficiles\u00a0\u00bb n\u2019est pas accord\u00e9 en nombre avec le mot singulier \u00ab\u00a0c'\u00a0\u00bb.",
#             "startIndex": 36,
#             "endIndex": 45,
#             "mistakeText": "difficiles",
#             "correctionText": "difficile",
#             "suggestions": [
#                 {
#                     "text": "difficile"
#                 }
#             ]
#         },
#         {
#             "group": "AutoCorrected",
#             "type": "Spelling",
#             "shortDescription": "Spelling Mistake",
#             "longDescription": "Faute de frappe possible trouv\u00e9e.",
#             "startIndex": 85,
#             "endIndex": 88,
#             "mistakeText": "etre",
#             "correctionText": "\u00eatre",
#             "suggestions": [
#                 {
#                     "text": "\u00eatre"
#                 }
#             ]
#         },
#         {
#             "group": "AutoCorrected",
#             "type": "Spelling",
#             "shortDescription": "Spelling Mistake",
#             "longDescription": "Faute de frappe possible trouv\u00e9e.",
#             "startIndex": 97,
#             "endIndex": 103,
#             "mistakeText": "vigilan",
#             "correctionText": "vigilant",
#             "suggestions": [
#                 {
#                     "text": "vigilant"
#                 }
#             ]
#         }
#     ],
#     "sentences": [],
#     "autoReplacements": [],
#     "stats": {
#         "textLength": 104,
#         "wordCount": 23,
#         "sentenceCount": 1,
#         "longestSentence": 104
#     }
# }