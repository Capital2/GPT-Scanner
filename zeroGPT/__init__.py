import requests
def zeroGPTVerdict(text:str)->dict:
    """
    this function return ``dict`` that contains:
    
    ``ai_percentage:`` how much of your text is ai generated 

    ``suspected_text:`` which part of your text is suspected to be ai generated
    
    ``additional_feedback:`` if your text is too short to get an accurate estimation this return a value
    """
    url = "https://api.zerogpt.com/api/detect/detectText"
    data = {
        "input_text": text
    }
    headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/json",
    "content-length": str(len(text)),
    "Origin": "https://www.zerogpt.com" 
    }
    response = requests.post(url,  headers=headers,json=data)
    
    response =  response.json()

    result = {
        "ai_percentage":response["data"]["fakePercentage"],
        "suspected_text":response["data"]["h"],
        "additional_feedback":response["data"]["additional_feedback"]
        }
    return result