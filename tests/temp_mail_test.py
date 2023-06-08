from mailgw_temporary_email import Email
from time import sleep
from re import findall

mail_client = Email()
mail_client.register()
mail_address = mail_client.address
print(mail_address)
input()
while True:
    sleep(5)
    try:
        message_id = mail_client.message_list()[0]['id']
        message = mail_client.message(message_id)
        verification_url = findall(r'https:\/\/u29261027\.ct\.sendgrid\.net\/ls\/click\?upn=\S+', message["text"])[1]
        if verification_url:
            break
    except IndexError as e:
        print(e) 
print(message["text"])
print(verification_url)
