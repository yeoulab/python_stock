import sys
import os
import hashlib
import hmac
import base64
import requests, json
import time

def make_signature():
    timestamp = int(time.time() * 1000)
    timestamp = str(timestamp)

    access_key = "VMum1ywUQcvjRM2m9pDL"                         # access key id (from portal or Sub Account)
    secret_key = "Rae9VY3lOlcUsLUavlzt34VL4TwXhDgCtviQKcjx"                             # secret key (from portal or Sub Account)
    secret_key = bytes(secret_key, 'UTF-8')

    method = "POST"
    uri = "/sms/v2/services/ncp:sms:kr:258079544481:yeoulab/messages"

    message = method + " " + uri + "\n" + timestamp + "\n" + access_key
    message = bytes(message, 'UTF-8')
    signingKey = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())

    url = "https://sens.apigw.ntruss.com/sms/v2/services/ncp:sms:kr:258079544481:yeoulab/messages"

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'x-ncp-apigw-timestamp': timestamp,
        'x-ncp-iam-access-key': access_key,
        'x-ncp-apigw-signature-v2': signingKey
    }

    data = {
        "type": "SMS",
        "contentType": "COMM",
        #"countryCode": "82",
        "from": "01024393039",
        #"subject": "string",
        "content": "string",
        "messages": [
            {
                "to": "01024393039",
                #"subject": "string",
                "content": "This message is sent by Python program for the test"
            }
        ]
        #"files": [
        #    {
        #        "name": "string",
        #        "body": "string"
        #    }
        #],
        #"reserveTime": "yyyy-MM-dd HH:mm",
        #"reserveTimeZone": "string",
        #"scheduleCode": "string"
    }

    res = requests.post(url, headers=headers, data=json.dumps(data))
    response = res.json()
    print(response)

    return signingKey


make_signature()