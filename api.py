from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request 
import os
import tmdbsimple as tmdb
from bs4 import BeautifulSoup
import requests, random
import re
import collections
import time

def createUrl(author: str, page: int) -> str:
    url = "https://letterboxd.com/" + author + "/watchlist/page/" + str(page) + "/"
    return url

def getImage(movie: int) -> str:
    tmdb.API_KEY = os.environ.get('THE_MOVIE_DB_API_KEY')

    movie = tmdb.Movies(movie)
    response = movie.info()
    link = movie.poster_path

    movieUrl = "https://image.tmdb.org/t/p/w300" + link

    return movieUrl

def getTitle(movie: int) -> str:
    tmdb.API_KEY = os.environ.get('THE_MOVIE_DB_API_KEY')

    movie = tmdb.Movies(movie)
    response = movie.info()
    title = movie.title

    return title

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

def getPageMovies(username: str, maxList: list, allMovies: list):
    pageNum = maxList.pop(random.randint(0, len(maxList) - 1))
    print(createUrl(username, pageNum))
    soup = BeautifulSoup(requests.get(createUrl(username, pageNum)).text, "html.parser")
    data = soup.find_all("li", {"class":"poster-container"})
    #if contains fail value return fail

    #print(data)
    for item in data:
        allMovies.append(item.find("div", {"class":"film-poster"})['data-film-slug'])

    return maxList, allMovies

def getMovie(username: list) -> list:
    starter = time.time()
    overlap = []
    maxPages = [] #contains the max page for each username
    allMovs = []
    randMovie = ""

    i = 0
    originalLength = len(username) #used to see if any names were removed
    length = len(username)
    invalidUsernames = []

    while i < length:
        if (validName(username[i])):
            invalidUsernames.append(username[i])
            username.pop(i)
            length-=1
        else:
            i+=1
    
    if length == 0:
        return "all usernames entered were invalid. Make sure they were all typed in correctly", 0

    if length < originalLength:
        randMovie += f"{invalidUsernames} usernames were invalid. Make sure they were all typed in correctly. The result for the correct usernames are "

    for name in username:
        maxPages.append(getMaxPage(name))
    
    pageLists = [] #list of lists containing the complete list of all usernames pages
    for num in maxPages:
        pageLists.append(createList(num))
    
    while(len(overlap) < 1 and bool(any(pageLists))):
        for i in range(len(pageLists)):
            ender = time.time()
            if (ender-starter) > 13:
                return "no matches found soon enough", 0
            if bool(pageLists[i]):
                pageLists[i], allMovs = getPageMovies(username[i], pageLists[i], allMovs)
        overlap = [item for item, count in collections.Counter(allMovs).items() if count >= len(username)]


    tmdbID = 0
    if (len(overlap) > 0):
        link = "https://letterboxd.com" + random.choice(overlap)
        soup = BeautifulSoup(requests.get(link).text, "html.parser")
        tmdbID = soup.find('body')['data-tmdb-id']
        randMovie = getTitle(tmdbID)

        
    else:
        randMovie += "the users have no overlapping movies in their watchlists"

    overlap.clear()
    maxPages.clear() 
    allMovs.clear()
    return randMovie, tmdbID

def validName(username):
    errorPage = BeautifulSoup(requests.get(createUrl(username, 1)).text, "html.parser")
    failure = errorPage.find_all("body", {"class":"error message-dark"})

    if len(failure) > 0:
        return True
    return False


app = Flask(__name__)
@app.route('/sms', methods=['POST'])
def send_sms():
    start = time.time()
    msg = request.values.get("Body").lower()
    message = msg.strip()
    if (message == 'format'):
        resp = MessagingResponse()
        end = time.time()
        msg = resp.message("type in any number of usernames seperated by a space or a non-valid character of your choice (ex. / or :) and" 
            + " then send and wait for a movie all users have in their watchlist")
        print(f"sent format in {end - start} seconds")


    else:
        usernames = re.findall("([A-Za-z_0-9.]+)", msg)
        
        result = getMovie(usernames)

        if (result[0] == "no matches found soon enough"):
            resp = MessagingResponse()
            msg = resp.message("we searched so much of your watchlists and couln't find any matches but you might have one just stop being such a movie nerd")
            print("couldn't find movie in time")
        else:
            resp = MessagingResponse()
            msg = resp.message(result[0])
            if result[1] != 0:
                msg.media(getImage(result[1]))
            end = time.time()
            print(f"sent result was {result} in {end - start} seconds")

    return str(resp)  
 
@app.route('/test')
def test():
    print("test")
    return("test")

@app.route('/fail')
def fail():
    resp = MessagingResponse()
    msg = resp.message("there is too much traffic. We recommend limiting the number of usernames you send in if you sent more than two or if a user has a watchlist that is more than 40 pages long.")
    print("fail") 
    return str(resp)       

if __name__ == "__main__":
    app.run(host='0.0.0.0')