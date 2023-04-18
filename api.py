from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from flask import Flask, request 
import os
import requests
import re
import time

app = Flask(__name__) 
@app.route('/sms', methods=['POST'])
def send_sms():
    start = time.time()
    msg = request.values.get("Body").lower()
    message = msg.strip()
    if (message == "repeat" or message == "\'repeat\'"):
        number = request.values.get("From")
        print(number)
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        client = Client(account_sid, auth_token)

        messages = client.messages.list(
                                    from_= number
                                )

        for message in messages:
            if (message.body.lower() != 'repeat'):
                repeatMsg = message.body.lower()
                break

        print(repeatMsg)
        users = re.findall("([A-Za-z_0-9.]+)", repeatMsg)
        url = 'https://watchlistpicker.com/api?users='
        url += '&u='.join(users)
        url += '&intersect=true'
        resp = MessagingResponse()
        try:
            response = requests.get(url).json()
            
        except:
            msg = resp.message('You have no overlapping movies in your watchlists.')
            print('no overlap')
            return str(resp)
        
        movie = response['film_name']
        msg = resp.message(movie)
        img = response['image_url']
        msg.media(img)
        end = time.time()
        print(f"received {message} and sent: {movie} in {end - start} seconds")
        return str(resp)

    elif (message == 'format' or message == '\'format\''):
        resp = MessagingResponse()
        end = time.time()
        msg = resp.message("Welcome to BoxdMe! \n To receive a movie just type in any number of usernames seperated by a space and then send! \n If you want to get another random movie with the same usernames, just type in 'repeat' \n If you want to see this message again just type in ‘format’")
        print(f"sent format in {end - start} seconds")
        return str(resp)
    
    else:
        users = re.findall("([A-Za-z_0-9.]+)", msg)
        url = 'https://watchlistpicker.com/api?users='
        url += '&users='.join(users)
        url += '&intersect=true'
        resp = MessagingResponse()
        try:
            response = requests.get(url).json()
            
        except:
            msg = resp.message('You have no overlapping movies in your watchlists.')
            print('no overlap')
            return str(resp)
        
        movie = response['film_name']
        msg = resp.message(movie)
        img = response['image_url']
        msg.media(img)
        end = time.time()
        print(f"received {message} and sent: {movie} in {end - start} seconds")
        return str(resp)

@app.route('/fail')
def fail():
    resp = MessagingResponse()
    msg = resp.message("there is too much traffic. We recommend limiting the number of usernames you send in if you sent more than two or if a user has a watchlist that is more than 40 pages long.")
    print("fail") 
    return str(resp)       

if __name__ == "__main__":
    app.run(host='0.0.0.0')