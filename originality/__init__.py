from dataclasses import dataclass, field
from mailgw_temporary_email import Email
from time import sleep
from re import findall, search
from fake_useragent import UserAgent
import requests
from faker import Faker
import secrets, string
import fileinput

# 1 credit for 50 words for the 2 apis combined (plagiarism and ai detection)
# 2500 words softlock for each email verified account

EMAIL_VERIF_URL = "https://core.originality.ai/api/user/email/verify"
USER_REGISTER_URL = "https://core.originality.ai/api/user/register"
CREATE_APIKEY_URL = "https://core.originality.ai/api/user/apiKeys/create"
API_BASE_URL = "https://api.originality.ai/api/v1/scan"
ACCOUNTS_PATH = "accounts.txt"


@dataclass
class OriginalityAiVerdict:
    public_link: str # root["public_link"]
    ai_score: float # root["ai"]["score"]["ai"]
    plagiarism_score: str # root["plagiarism"]["total_text_score"]
    credits_remaining: int # root["credits"]

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
                else:
                    print(line, end='')


class OriginalityAccount:
    @staticmethod
    def create(save_account=True) -> OriginalityAccountData :

        mail_client = Email()
        mail_client.register()
        mail_address = mail_client.address
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
            raise ValueError(f"problem with registring HTTP: {r.status_code}")
        # verify email
        while True:
            sleep(1)
            try:
                message_id = mail_client.message_list()[0]['id']
                message = mail_client.message(message_id)
                verification_url = findall(r'https:\/\/u29261027\.ct\.sendgrid\.net\/ls\/click\?upn=\S+', message["text"])[1]
                if verification_url:
                    break
                else:
                    raise ValueError(f"email received but didn't match template instead matched: {verification_url}")
            except IndexError as e:
                print("waiting...") # needs to be properly logged
        
        # the url return 302
        # so we get the new  location url that has token
        r = client.get(verification_url)
        # r.url is the new url (requests follows redirection by default)
        token = search(r'(?<=\?token=).*', r.url)
        r = client.get(f"{EMAIL_VERIF_URL}?token={token.group(0)}")

        acc.active_apikey = OriginalityAccount.__create_api_key(client, acc.access_token)
        if save_account:
            with open('accounts.txt', 'a') as f:
                f.write(f'{acc.credit_count}::{acc.active_apikey}::{acc.email}::{acc.password}\n')
        return acc

    @staticmethod
    def __create_api_key(client: requests.Session, access_token: str) -> str :
        client.headers.update({
            "Authorization": f"Bearer {access_token}"
        })
        r = client.post(CREATE_APIKEY_URL)
        return r.json()["api_key"]["api_token"]
    
    @staticmethod
    def get_from_local(min_credits = 50) -> OriginalityAccountData | None:
        with open(ACCOUNTS_PATH, 'r') as f:
            line = f.readline()
            while line:
                linetab = line.rstrip().split('::')

                if len(linetab) != 4 :
                    print("cannot use this line as there somehow too many fields")
                    # needs to be logged
                    continue

                if int(linetab[0]) >= min_credits :
                    return OriginalityAccountData(
                        name="",
                        _credit_count=linetab[0],
                        active_apikey=linetab[1],
                        email=linetab[2],
                        password=linetab[3],
                        access_token=""
                    )
                
                line = f.readline()
        return None


class Verdict:
    @staticmethod
    def get(
        content:str,
        account_data: OriginalityAccountData,
        check_plagiarism = True,
        check_ai = True) -> OriginalityAiVerdict :
        
        if not (check_plagiarism and check_ai):
            raise ValueError("check_plagiarism and check_ai cannot be both set to false")
        if (check_plagiarism and check_ai):
            endpoint = "/ai-plag"
        elif (check_plagiarism):
            endpoint = "plag"
        else:
            endpoint = "ai"
        
        payload = {
            "content": content
        }

        headers = {
            'X-OAI-API-KEY': account_data.active_apikey
        }
        r = requests.post(API_BASE_URL + endpoint, headers=headers, json=payload)

        if not r:
            raise Exception(f"{API_BASE_URL + endpoint} returned with error code: {r.status_code}")
        jsonresponse = r.json()
        res = OriginalityAiVerdict(
            public_link= jsonresponse["public_link"],
            ai_score= jsonresponse["ai"]["score"]["ai"],
            plagiarism_score= jsonresponse["plagiarism"]["total_text_score"],
            credits_remaining= jsonresponse["credits"]
        )
        acc.credit_count = res.credits_remaining
        return res


if __name__ == "__main__":

    content = "The first person to use the concept of a singularity in the technological context was the 20th-century Hungarian-American mathematician John von Neumann.Stanislaw Ulam reports in 1958 an earlier discussion with von Neumann centered on the accelerating progress of technology and changes in the mode of human life, which gives the appearance of approaching some essential singularity in the history of the race beyond which human affairs, as we know them, could not continue Subsequent authors have echoed this viewpoint.The concept and the term singularity were popularized by Vernor Vinge first in 1983 in an article that claimed that once humans create intelligences greater than their own, there will be a technological and social transition similar in some sense to the knotted space-time at the center of a black hole and later in his 1993 essay The Coming Technological Singularity, in which he wrote that it would signal the end of the human era, as the new superintelligence would continue to upgrade itself and would advance technologically at an incomprehensible rate. He wrote that he would be surprised if it occurred before 2005 or after 2030. Another significant contributor to wider circulation of the notion was Ray Kurzweil's 2005 book The Singularity Is Near, predicting singularity by 2045."
    estimated_credits = -(sum(1 for c in content if c in ' \t\n') // -50) # estimated if ai+plagiat (also the negatives make a ciel)

    acc = OriginalityAccount.get_from_local(estimated_credits)
    if not acc:
        acc = OriginalityAccount.create()
    print(acc)
    
    verdict = Verdict.get(content, acc)
    print(verdict)