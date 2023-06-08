from dataclasses import dataclass, field
from mailgw_temporary_email import Email
from time import sleep
from re import findall, search
from fake_useragent import UserAgent
import requests
from requests import RequestException, cookies
from faker import Faker
import secrets, string
import fileinput
import logging
from retrying import retry

ACCOUNTS_PATH = "data/zeroaccounts.txt"
LOG = logging.getLogger(__name__)
SIGNUP_URL = "https://lydqhgdzhvsqlcobdfxi.supabase.co/auth/v1/signup"
LOGIN_URL = "https://lydqhgdzhvsqlcobdfxi.supabase.co/auth/v1/token?grant_type=password"
API_ENDPOINT_URL = "https://api.gptzero.me/v2/predict/text"
GENERIC_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx5ZHFoZ2R6aHZzcWxjb2JkZnhpIiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODA5MTMyNDUsImV4cCI6MTk5NjQ4OTI0NX0.fiun9l_A2j_tHza1j8W_bEAHHj4NzS1PdpL3RX4-eWc"
HISTORY_URL = "https://api.gptzero.me/v2/user/callHistory"

@dataclass
class ZeroAccountData:
    email: str
    password: str
    authcookie: str = field(repr=False, init="")

@dataclass
class ZeroVerdictData:
    average_generated_prob: float
    completely_generated_prob: float
    overall_burstiness: float

class ZeroAccount:

    @staticmethod
    @retry(
        # wait_fixed=5000,
        stop_max_attempt_number=2,
        retry_on_exception=lambda e: isinstance(e, RequestException) or isinstance(e, ValueError),
    )
    def create(save_account=True) -> ZeroAccountData | None:
        mail_client = Email()
        mail_client.register()
        mail_address = mail_client.address

        # not needed but for the heck of it
        fake = Faker()

        client = requests.session()
        headers = {
            'authority': 'https://gptzero.me/',
            'accept': 'text/event-stream',
            'accept-language': 'en,fr-FR;q=0.9,fr;q=0.8,es-ES;q=0.7,es;q=0.6,en-US;q=0.5,am;q=0.4,de;q=0.3',
            'cache-control': 'no-cache',
            'referer': 'https://gptzero.me/',
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': UserAgent().random,
        }
        
        alphabet = string.ascii_letters + string.digits + string.punctuation
        acc = ZeroAccountData(
            email=mail_address,
            password=''.join(secrets.choice(alphabet) for i in range(20)),
        )
        name = fake.name().replace(" ", "").replace(".", "")
        payload = {
            "data": {
                "first_name":name,
                "last_name":"",
                "full_name":name,
                "org":"",
                "email":acc.email,
                "org_role":"Student",
                "industry":""
                },
            "email":acc.email,
            "gotrue_meta_security": {},
            "password": acc.password
        }
        client.headers.update({
            "apiKey": GENERIC_TOKEN,
            "authorization": f"Bearer {GENERIC_TOKEN}"
        })
        r = client.post(url=SIGNUP_URL, json=payload)
        if not r:
            LOG.error(f"FATAL: could not register with {acc} with reponse: {r.text}\nretrying ...")
            raise RequestException(f"problem with registring HTTP: {r.status_code} check logs for more info")
        # mail verif
        while True:
            sleep(0.5)
            LOG.debug(f"in true while loop")
            try:
                message_id = mail_client.message_list()[0]['id']
                message = mail_client.message(message_id)
                verification_url = findall(r'https:\/\/lydqhgdzhvsqlcobdfxi\.supabase\.co\/auth\/v1\/verify\?token=\S+', message["text"])[0]
                if verification_url:
                    break
                else:
                    LOG.error(f"FATAL: didn't find verification link in message: {message['text']} \nretrying ...")
                    raise ValueError(f"email received but didn't match template check logs")
            except IndexError as e:
                LOG.info("waiting for verification email")
        
        # getting auth cookie no redirects
        client.get(verification_url, allow_redirects=False)
        acc.authcookie = client.cookies['sb-access-token']

        client.headers.update({
            "authorization": f"Bearer {acc.authcookie}"
        })
        r = client.get(HISTORY_URL)
        # check if we're logged in (make the server reply with our email)
        r = client.get(f"https://lydqhgdzhvsqlcobdfxi.supabase.co/rest/v1/profiles?select=email&email=eq.{acc.email}")
        if not r.json()[0]["email"] == acc.email:
            LOG.error(f"failed to log in with account {acc}")
            return None
            # add handling
            
        LOG.info(f"account created successfully: {acc}")

        if save_account:
            LOG.debug(f"saving account")
            with open(ACCOUNTS_PATH, 'a') as f:
                line = f'{acc.email}::{acc.password}\n'
                f.write(line)
                LOG.debug(f"written line {line} in {ACCOUNTS_PATH}")
                LOG.info(f"account saved in {ACCOUNTS_PATH}")
        return acc
    
    @staticmethod
    def get_from_local() -> ZeroAccountData | None:

        with open(ACCOUNTS_PATH, 'r') as f:
            line = f.readline()
            ret = None
            while line:
                linetab = line.rstrip().split('::')

                if len(linetab) != 2 :
                    LOG.warning(f"{line} in {ACCOUNTS_PATH} has too many or too few fields: expected 2 found {len(linetab)}")
                    continue

                ret = ZeroAccountData(
                    email=linetab[0],
                    password=linetab[1]
                )
                LOG.debug(f"loaded {ret}")
                break
            line = f.readline()
        if not ret:
            LOG.info(f"no saved account found")
            return None

        # login
        client = requests.Session()
        client.headers = client.headers = {
            'authority': 'https://gptzero.me/',
            'accept': 'text/event-stream',
            'accept-language': 'en,fr-FR;q=0.9,fr;q=0.8,es-ES;q=0.7,es;q=0.6,en-US;q=0.5,am;q=0.4,de;q=0.3',
            'cache-control': 'no-cache',
            'referer': 'https://gptzero.me/',
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': UserAgent().random,
            "apikey": f"{GENERIC_TOKEN}",
            "content-type": "application/json"
        }
        payload = {
            "data": {},
            "email": ret.email,
            "gotrue_meta_security": {},
            "password": ret.password
        }
        r = client.post(LOGIN_URL, json=payload)
        token = r.json()["access_token"]

        client.headers.update({
            "apikey": token
        })
        client.cookies.update({
            "sb-access-token": token
        })
        r = client.get(HISTORY_URL)
        print(r.json())
        if token:
            ret.authcookie = token
            LOG.info(f"Login successful with account {ret}")
            LOG.debug(f"cookie returned:\n{token} ")
            return ret
        
        LOG.error(f"No access token in response:\n{r.json()}")
        return None

class ZeroVerdict:

    @staticmethod
    def get(content : str, account_data: ZeroAccountData):
        client = requests.session()
        client.headers = {
            'authority': 'https://gptzero.me/',
            'accept': 'text/event-stream',
            'accept-language': 'en,fr-FR;q=0.9,fr;q=0.8,es-ES;q=0.7,es;q=0.6,en-US;q=0.5,am;q=0.4,de;q=0.3',
            'cache-control': 'no-cache',
            'referer': 'https://gptzero.me/',
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': UserAgent().random,
            "authorization": f"Bearer {account_data.authcookie}",
            "apikey": account_data.authcookie
        }
        payload = {
            "document": content
        }
        r = requests.post(API_ENDPOINT_URL, json=payload)
        jsonresponse = r.json()
        LOG.debug(f"Api response: {jsonresponse}")
        
        res = ZeroVerdictData(
            average_generated_prob=jsonresponse["documents"][0]["average_generated_prob"],
            completely_generated_prob=jsonresponse["documents"][0]["completely_generated_prob"],
            overall_burstiness=jsonresponse["documents"][0]["overall_burstiness"]
        )

        LOG.info(f"return data generated successfully: {res}")
        return res


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    acc = ZeroAccount.get_from_local()
    if not acc:
        acc = ZeroAccount.create()
    
    content = "The first person to use the concept of a singularity in the technological context was the 20th-century Hungarian-American mathematician John von Neumann.Stanislaw Ulam reports in 1958 an earlier discussion with von Neumann centered on the accelerating progress of technology and changes in the mode of human life, which gives the appearance of approaching some essential singularity in the history of the race beyond which human affairs, as we know them, could not continue Subsequent authors have echoed this viewpoint.The concept and the term singularity were popularized by Vernor Vinge first in 1983 in an article that claimed that once humans create intelligences greater than their own, there will be a technological and social transition similar in some sense to the knotted space-time at the center of a black hole and later in his 1993 essay The Coming Technological Singularity, in which he wrote that it would signal the end of the human era, as the new superintelligence would continue to upgrade itself and would advance technologically at an incomprehensible rate. He wrote that he would be surprised if it occurred before 2005 or after 2030. Another significant contributor to wider circulation of the notion was Ray Kurzweil's 2005 book The Singularity Is Near, predicting singularity by 2045."
    res = ZeroVerdict.get(content, acc)
