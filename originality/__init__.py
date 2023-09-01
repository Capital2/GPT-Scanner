from dataclasses import dataclass, field
from mailgw_temporary_email import Email
from time import sleep
from re import findall, search
from fake_useragent import UserAgent
import requests
from requests import RequestException
from faker import Faker
import secrets, string
import fileinput
import logging
from retrying import retry
import os, sys
from .sentence_split import split_into_sentences

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
# 1 credit for 50 words for the 2 apis combined (plagiarism and ai detection)
# 2500 words softlock for each email verified account

EMAIL_VERIF_URL = "https://core.originality.ai/api/user/email/verify"
USER_REGISTER_URL = "https://core.originality.ai/api/user/register"
USER_ACCOUNT_INFO = "https://core.originality.ai/api/user/account"
USER_LOGIN_URL = "https://core.originality.ai/api/user/login"
CREATE_APIKEY_URL = "https://core.originality.ai/api/user/apiKeys/create"
API_BASE_URL = "https://api.originality.ai/api/v1/scan"
FREE_API_URL = "https://core.originality.ai/api/user/content-scans"
ACCOUNTS_PATH = "data/accounts.txt"
LOG = logging.getLogger(__name__)

@dataclass
class OriginalityVerdictData:
    public_link: str # root["public_link"]
    ai_score: float # root["ai"]["score"]["ai"]
    plagiarism_score: str # root["plagiarism"]["total_text_score"]

@dataclass
class OriginalityAccountData:
    name: str
    email: str
    password: str
    access_token: str = field(repr=False)
    _credit_count: int = 50
    active_apikey : str = ""

    @property
    def credit_count(self) -> int:
        return self._credit_count

    @credit_count.setter
    def credit_count(self, value):
        self._credit_count = value
        # try to update in accounts.txt
        if not self.email:
            return
        with fileinput.input(ACCOUNTS_PATH, inplace=True) as f:
            for line in f:
                if line.find(self.email) > -1:
                        tab = line.split("::")
                        tab[0] = str(value)
                        print('::'.join(tab), end='') # fileinput prints to the file
                        LOG.debug(f"found target: updated {ACCOUNTS_PATH} with {line} in setter")
                else:
                    print(line, end='')
                    LOG.debug(f"updated {ACCOUNTS_PATH} with {line} in setter")


class OriginalityAccount:

    @staticmethod
    @retry(
        # wait_fixed=5000,
        stop_max_attempt_number=2,
        retry_on_exception=lambda e: isinstance(e, RequestException) or isinstance(e, ValueError),
    )
    def create(save_account=True) -> OriginalityAccountData :

        mail_client = Email()
        mail_client.register()
        mail_address = mail_client.address

        # not needed but for the heck of it
        fake = Faker()

        client = requests.session()
        client.headers = {
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

        alphabet = string.ascii_letters + string.digits + string.punctuation
        acc = OriginalityAccountData(
            name=fake.name().replace(" ", "").replace(".", ""),
            email=mail_address,
            password= ''.join(secrets.choice(alphabet) for i in range(20)),
            access_token=""
        )
        payload = {
            "name":acc.name,
            "email":acc.email,
            "password":acc.password,
            "captcha": "null"
        }
        r = client.post(url=USER_REGISTER_URL, json=payload)
        if r :
            acc.access_token = r.json()["auth_data"]["access_token"]
        else:
            LOG.error(f"FATAL: could not register with {acc} with error text {r.text}\nretrying ...")
            raise RequestException(f"problem with registring HTTP: {r.status_code} check logs for more info")
        # verify email
        while True:
            sleep(0.5)
            LOG.debug(f"in true while loop")
            try:
                message_id = mail_client.message_list()[0]['id']
                message = mail_client.message(message_id)
                verification_url = findall(r'https:\/\/u29261027\.ct\.sendgrid\.net\/ls\/click\?upn=\S+', message["text"])[1]
                if verification_url:
                    break
                else:
                    LOG.error(f"FATAL: didn't find verification link in message: {message['text']} \nretrying ...")
                    raise ValueError(f"email received but didn't match template check logs")
            except IndexError as e:
                LOG.info("waiting for verification email")
        
        # the url return 302
        # so we get the new  location url that has token
        r = client.get(verification_url)
        LOG.debug(f"{r.status_code} redirected to {r.url}")
        # r.url is the new url (requests follows redirection by default)
        token = search(r'(?<=\?token=).*', r.url)
        verif = f"{EMAIL_VERIF_URL}?token={token.group(0)}"
        r = client.get(verif)

        LOG.info(f"verification with {verif} returned {r.text} with code {r.status_code}")

        # needs a check here
        acc.active_apikey = OriginalityAccount.__create_api_key(client, acc.access_token)
        if save_account:
            LOG.debug(f"saving account")
            with open(ACCOUNTS_PATH, 'a+') as f:
                line = f'{acc.credit_count}::{acc.active_apikey}::{acc.email}::{acc.password}\n'
                f.write(line)
                LOG.debug(f"written line {line} in {ACCOUNTS_PATH}")
        
        LOG.info(f"account created successfully: {acc}")
        return acc

    @staticmethod
    def __create_api_key(client: requests.Session, access_token: str) -> str :
        client.headers.update({
            "Authorization": f"Bearer {access_token}"
        })
        r = client.post(CREATE_APIKEY_URL)

        LOG.debug(f"api key creation returned with {r.json()}")
        return r.json()["api_key"]["api_token"]
    
    @staticmethod
    def _login(account_data: OriginalityAccountData) -> OriginalityAccountData | None:
        if hasattr(account_data, 'access_token') and account_data.access_token:
            return account_data
        
        client = requests.session()
        client.headers = {
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

        payload = {
            "email":account_data.email,
            "password":account_data.password,
            "captcha": "null"
        }

        r = client.post(url=USER_LOGIN_URL, json=payload)
        if r :
            account_data.access_token = r.json()["auth_data"]["access_token"]
            LOG.info(f"Login successful with account {account_data}")
        else:
            LOG.error(f"FATAL: could not login with {account_data} with error text {r.text}")
        
        return account_data


    @staticmethod
    def get_from_local(min_credits = 50) -> OriginalityAccountData | None:
        if not os.path.exists(ACCOUNTS_PATH):
            return None
        with open(ACCOUNTS_PATH, 'r') as f:
            line = f.readline()
            while line:
                linetab = line.rstrip().split('::')

                if len(linetab) != 4 :
                    LOG.warning(f"{line} in {ACCOUNTS_PATH} has too many or too few fields: expected 4 found {len(linetab)}")
                    continue

                if int(linetab[0]) >= min_credits :
                    ret = OriginalityAccountData(
                        name="",
                        _credit_count=int(linetab[0]),
                        active_apikey=linetab[1],
                        email=linetab[2],
                        password=linetab[3],
                        access_token=""
                    )
                    LOG.debug(f"returning {ret} as {linetab[0]} >= {min_credits}")
                    return ret
                line = f.readline()
        LOG.info(f"none of the saved accounts had credits over {min_credits}")
        return None


class OriginalityVerdict:
    @staticmethod
    def get(
        content:str,
        account_data: OriginalityAccountData,
        check_plagiarism = True,
        check_ai = True) -> OriginalityVerdictData :

        if not (check_plagiarism or check_ai):
            LOG.warning("check_plagiarism and check_ai cannot be both set to false, setting check_ai to True")
            check_ai = True
        if (check_plagiarism and check_ai):
            endpoint = "/ai-plag"
        elif (check_plagiarism):
            endpoint = "/plag"
        else:
            endpoint = "/ai"
        
        payload = {
            "content": content
        }

        headers = {
            'X-OAI-API-KEY': account_data.active_apikey
        }
        r = requests.post(API_BASE_URL + endpoint, headers=headers, json=payload)

        if not r:
            LOG.error(f"POST {API_BASE_URL + endpoint} returned {r.text}")
            raise RequestException(f"error: {r.json()['error']}")
        jsonresponse = r.json()
        LOG.debug(f"Api response: {jsonresponse}")
        res = OriginalityVerdictData(
            public_link= jsonresponse["public_link"],
            ai_score= jsonresponse["ai"]["score"]["ai"] if check_ai else -1,
            plagiarism_score= jsonresponse["plagiarism"]["total_text_score"] if check_plagiarism else -1
        )
        account_data.credit_count = jsonresponse["credits"]
        LOG.info(f"api request complete with result {res}")
        return res

    @staticmethod
    def free_get(content:str,
        account_data: OriginalityAccountData,
        check_plagiarism = True,
        check_ai = True) -> str :

        if not account_data.access_token:
            account_data = OriginalityAccount._login(account_data)

        # the plagiarism detector needs a sentences breackdown to operate
        # the current split_into_sentences function is anglophone
        payload = {
            "originalContent": content,
            "scanType": 0,
            "aiModelVersion": 1,
            "creditCost": 3,
            "sentences": split_into_sentences(content)
            
        }
        headers = {
            "Authorization": f"Bearer {account_data.access_token}",

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

        r = requests.post(FREE_API_URL, headers=headers, json=payload)
        if not r:
            LOG.error(f"POST {FREE_API_URL} returned {r.text}")
            raise RequestException(f"error: {r.json()['error']}")
        jsonresponse = r.json()

        LOG.debug(f"Api response: {jsonresponse}")
        res = OriginalityVerdictData(
            public_link= f"https://app.originality.ai/content-scan/{jsonresponse['scanID']}",
            ai_score= jsonresponse["ai_detection"]["fake"] if check_ai else -1,
            plagiarism_score= jsonresponse["plagiarism_score"] if check_plagiarism else -1
        )
        LOG.info(f"api request complete with result {res}")

        account_data.credit_count = requests.get(USER_ACCOUNT_INFO, headers=headers).json()["credits"]["current_credits"]
        LOG.info(f"credits remaining: {account_data.credit_count}")
        return res



if __name__ == "__main__":
    # TODO: divide to sentences, so the plagiarism works
    logging.basicConfig(level=logging.INFO)
    content="""
Any identifier of the form __spam (at least two leading underscores, at most one trailing underscore) is textually replaced with _classname__spam, where classname is the current class name with leading underscore(s) stripped. This mangling is done without regard to the syntactic position of the identifier, so it can be used to define class-private instance and class variables, methods, variables stored in globals, and even variables stored in instances. private to this class on instances of other classes.

And a warning from the same page:

Name mangling is intended to give classes an easy way to define “private” instance variables and methods, without having to worry about instance variables defined by derived classes, or mucking with instance variables by code outside the class. Note that the mangling rules are designed mostly to avoid accidents; it still is possible for a determined soul to access or modify a variable that is considered private.

"""
    estimated_credits = -(sum(1 for c in content if c in ' \t\n') // -50) # estimated if ai+plagiat (also the negatives make a ciel)

    acc = OriginalityAccount.get_from_local(estimated_credits)
    if not acc:
        acc = OriginalityAccount.create()
    
    verdict = OriginalityVerdict.free_get(content, acc)
    print(verdict)

