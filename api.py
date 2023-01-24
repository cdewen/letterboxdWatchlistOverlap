from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request 
from bs4 import BeautifulSoup
import requests, random
import re
import collections


final = []
def createUrl(author: str, page: int) -> str:
    url = "https://letterboxd.com/" + author + "/watchlist/page/" + str(page) + "/"
    return url

def getWatchlist(username: str) -> list:
    ret = []
    page = [1]
    maxPage: int = 1
    req = BeautifulSoup(requests.get(createUrl(username, 1)).text, "lxml")
    req = requests.get(createUrl(username,1))
    req = BeautifulSoup(req.content)
    pageCount = req.find_all("li", {"class":"paginate-page"})

    for item in pageCount:
        if (item.get_text() == '…'):
            pass
        else: 
            page.append(int(item.get_text()))

    maxPage = max(page)

    i = 1
    while i <= maxPage:
        print(createUrl(username, i))
        soup = BeautifulSoup(requests.get(createUrl(username, i)).text, "lxml")
        data = soup.find_all("li", {"class":"poster-container"})

        for item in data:
            final.append(str(item.find("img", {"class":"image"})['alt']).encode("ascii", errors="ignore").decode("utf-8"))
        i+=1

    return ret

app = Flask(__name__)
@app.route('/sms', methods=['POST'])
def send_sms():
    #incoming message
    msg = request.values.get("Body").lower()
    if (msg == 'format'):
        res = MessagingResponse()
        res.message("type in any number of usernames seperated by a space or a non-valid character of your choice (ex. / or :) and" 
            + " then send and wait for a movie all users have in their watchlist")
    else:
        usernames = re.findall("([A-Za-z_0-9.]+)", msg)

        for name in usernames:
            getWatchlist(name)

        if (len(final) < 1):
            res = MessagingResponse()
            res.message("there are no overlapping movies in the users' watchlists")
                
        else:
            fin = [item for item, count in collections.Counter(final).items() if count >= len(usernames)]
            randMovie = random.choice(fin)
            res = MessagingResponse()
            res.message(randMovie)

    return str(res)  

@app.route('/test')
def index():
    return "server connected"          

if __name__ == "__main__":
    app.run(host='0.0.0.0')


