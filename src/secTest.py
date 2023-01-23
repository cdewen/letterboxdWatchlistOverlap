from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request 
from bs4 import BeautifulSoup
import requests, random
import re

def createUrl(author: str, page: int) -> str:
    url = "https://letterboxd.com/" + author + "/watchlist/page/" + str(page) + "/"
    return url

def getWatchlist(username: str) -> list:
    ret = []
    page = [1]
    maxPage: int = 1
    req = BeautifulSoup(requests.get(createUrl(username, 1)).text, "lxml")
    #or can be
    #req = requests.get(createUrl(username,1))
    #req = BeautifulSoup(req.content)
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
        #or can be
        #soup = requests.get(createUrl(username,1))
        #soup = BeautifulSoup(req.content)
        data = soup.find_all("li", {"class":"poster-container"})

        for item in data:
            ret.append(str(item.find("img", {"class":"image"})['alt']).encode("ascii", errors="ignore").decode("utf-8"))
        i+=1

    return ret

app = Flask(__name__)
@app.route('/sms', methods=['POST'])
def send_sms():
    #incoming message
    msg = request.values.get("Body").lower()
    usernames = re.findall("([A-Za-z_0-9.]+)", msg)


    retOne = getWatchlist(usernames[0])
    retTwo = getWatchlist(usernames[1])

    #set = set(retOne).intersection(set(retTwo))
    fin = set(retOne).intersection(set(retTwo))
    final = list(fin)

    randMovie = random.choice(final)

    res = MessagingResponse()
    res.message(randMovie)
    return str(res)

if __name__ == '__main__':
    app.run(debug=True)


