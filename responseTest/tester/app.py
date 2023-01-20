from flask import Flask, Response, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
from bs4 import BeautifulSoup
import random
import re


app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    body = request.values.get('Body')
    body = str

    resp = MessagingResponse()

    usernames = re.findall("([A-Za-z_0-9.]+)", body)

    resp.message(str(usernames[0]))

    return Response(str(resp), mimetype='application/xml')

if __name__ == '__main__':
    app.run(debug=True)