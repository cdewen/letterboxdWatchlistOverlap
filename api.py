from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request 
from bs4 import BeautifulSoup
import requests, random
import re
import collections
import time


allMovies = []
def createUrl(author: str, page: int) -> str:
    url = "https://letterboxd.com/" + author + "/watchlist/page/" + str(page) + "/"
    return url

def createList(r2):
    r1=1
    res = []
    if (r1 == r2):
        res.append(r1)
    else:
        while(r1 < r2+1 ):
            res.append(r1)
            r1 += 1
    return res

def getMaxPage(username):
    pageOne = [1]
    req = BeautifulSoup(requests.get(createUrl(username, 1)).text, "html.parser")
    pageCount = req.find_all("li", {"class":"paginate-page"})

    for item in pageCount:
        if (item.get_text() == '…'):
            pass
        else: 
            pageOne.append(int(item.get_text()))

    return max(pageOne)

def getPageMovies(username: str, maxList: list):
    pageNum = maxList.pop(random.randint(0, len(maxList) - 1))
    print(createUrl(username, pageNum))
    soup = BeautifulSoup(requests.get(createUrl(username, pageNum)).text, "html.parser")
    data = soup.find_all("li", {"class":"poster-container"})

    for item in data:
        allMovies.append(str(item.find("img", {"class":"image"})['alt']).encode("ascii", errors="ignore").decode("utf-8"))
    return maxList

def getMovie(username: list) -> list:
    overlap = []
    overlap.clear()
    allMovies.clear()
    maxPages = [] #contains the max page for each username
    for name in username:
        maxPages.append(getMaxPage(name))
    
    pageLists = [] #list of lists containing the complete list of all usernames pages
    for num in maxPages:
        pageLists.append(createList(num))
    
    while(len(overlap) < 1 and bool(any(pageLists))):
        for i in range(len(pageLists)):
            if bool(pageLists[i]):
                pageLists[i] = getPageMovies(username[i], pageLists[i])
        overlap = [item for item, count in collections.Counter(allMovies).items() if count >= len(username)]


    if (len(overlap) > 0):
        randMovie = random.choice(overlap)
    else:
        randMovie = "the users have no overlapping movies in their watchlists"
    allMovies.clear()
    overlap.clear()
    return randMovie

app = Flask(__name__)
@app.route('/sms', methods=['POST'])
def send_sms():
    start = time.time()
    allMovies.clear()
    msg = request.values.get("Body").lower()
    message = msg.strip()
    if (message == 'format'):
        res = MessagingResponse()
        end = time.time()
        allMovies.clear()
        res.message("type in any number of usernames seperated by a space or a non-valid character of your choice (ex. / or :) and" 
            + " then send and wait for a movie all users have in their watchlist")
        print(f"sent format in {end - start} seconds")

    else:
        allMovies.clear()
        usernames = re.findall("([A-Za-z_0-9.]+)", msg)
        
        result = getMovie(usernames)

        res = MessagingResponse()
        res.message(result)
        allMovies.clear()
        end = time.time()
        print(f"sent {result} as the random movie between {str(usernames)} in {end - start} seconds")

    return str(res)  

@app.route('/test')
def index():
    return "work!!!" 

@app.route('/fail')
def fail():
    res = MessagingResponse()
    res.message("there is too much traffic. We recommend limiting the number of usernames you send in if you sent more than two or if a user has a watchlist that is more than 40 pages long.")
    print("fail") 
    return "failure"       

if __name__ == "__main__":
    app.run(host='0.0.0.0')


