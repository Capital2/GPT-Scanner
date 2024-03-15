import requests
import urllib.parse as parser
import logging
from bs4 import BeautifulSoup

LOG = logging.getLogger(__name__)

class Paraphraser():

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            LOG.info("Launched Paraphraser service")
            cls.instance = super(Paraphraser, cls).__new__(cls)
            cls.instance.session = requests.Session()

            response = cls.instance.session.get("https://www.paraphrasing.io/")
            cookie = parser.unquote(response.cookies.get("laravel_9_session"))

            soup = BeautifulSoup(response.content, 'html.parser')
            token_input = soup.find("input", {"name": "_token"})
            token = token_input.get("value")
            headers = {
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-CSRF-TOKEN": token,
                "X-Requested-With": "XMLHttpRequest",
                "Cookie": f"laravel_9_session={cookie}"                
            }
            cls.instance.session.headers.update(headers) 
        return cls.instance
    
    def __renew_token(self):
        response = self.instance.session.get("https://www.paraphrasing.io/")
        
        cookie = parser.unquote(response.cookies.get("laravel_9_session"))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        token_input = soup.find("input", {"name": "_token"})
        self.instance.token = token_input.get("value")
        headers = {
            "X-CSRF-TOKEN": self.instance.token,
            "Cookie": f"laravel_9_session={cookie}"                
        }
        self.instance.session.headers.update(headers)

    def paraphrase(self,data:str,lang:str,mode:str)->str:
        data = parser.quote_plus(data)
        body = f"paragraph={data}&lang={lang}&mode={mode}&is_primium=0"
        
        response = self.instance.session.post("https://www.paraphrasing.io/paraphras",data=body)  
        if response.status_code == 200:
            result = response.json()['result']
            return self.__parse_content(result)
        elif response.status_code == 419:
            # if more than twice tnekna
            LOG.warning("scary recursive call, renewing token ...")
            self.__renew_token()
            return self.paraphrase(data,lang,mode)
        else:
            return None
        
    def __parse_content(self,data):
        data = data.replace("<b>","").replace("</b>","").replace("<br>","")
        return data