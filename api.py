from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request, render_template
from bs4 import BeautifulSoup
import requests, random
import re
import collections
import time

def getFriends(username: str) -> list:
    start = time.time()
    urlFollowing = "https://letterboxd.com/" + username + "/following/"
    urlFollowers = "https://letterboxd.com/" + username + "/followers/"

    followingData = BeautifulSoup(requests.get(urlFollowing).text, "html.parser")
    followingUsernames = followingData.find_all("td", {"class":"table-person"})
    following = followingData.find_all("a", {"class":"name"})

    followerData = BeautifulSoup(requests.get(urlFollowers).text, "html.parser")
    followerUsernames = followerData.find_all("td", {"class":"table-person"})
    followers = followerData.find_all("a", {"class":"name"})

    usernameList = []
    usernameData = []

    for username in followerUsernames:
        usernameList.append(username.find("a", {"class":"name"})['href'])

    for username in usernameList:
        usernameData.append(username.replace("/",""))

    usernameList.clear()

    for username in followingUsernames:
        usernameList.append(username.find("a", {"class":"name"})['href'])

    for username in usernameList:
        usernameData.append(username.replace("/",""))

    usernames = [item for item, count in collections.Counter(usernameData).items() if count >= 2]

    data = followers + following

    all = []

    for item in data:
        all.append((item.getText()).strip())

    friendNames = [item for item, count in collections.Counter(all).items() if count >= 2]

    avatars = []

    images = followerData.find_all("a", {"class":"avatar -a40"})

    for image in images:
        if image.find("img")['alt'] in friendNames:
           avatars.append(image.find("img")['src'])

    end = time.time()

    print(end - start)
    
    return friendNames, avatars, usernames

def createUrl(author: str, page: int) -> str:
    url = "https://letterboxd.com/" + author + "/watchlist/page/" + str(page) + "/"
    return url

def getImage(movie: str) -> str:
    movie = movie.lower()
    movie = movie.replace(" ", "-")
    url = "https://letterboxd.com/film/" + movie + "/"

    soup = str(BeautifulSoup(requests.get(url).text, "html.parser"))

    movieUrl = re.findall("(?<=image\":\")([^\"]+)", soup)

    return movieUrl[0]

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

    for item in data:
        allMovies.append(str(item.find("img", {"class":"image"})['alt']).encode("ascii", errors="ignore").decode("utf-8"))
    return maxList, allMovies

def getMovie(username: list) -> list:
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
        return "all usernames entered were invalid. Make sure they were all typed in correctly"

    if length < originalLength:
        randMovie += f"{invalidUsernames} usernames were invalid. Make sure they were all typed in correctly. The result for the correct usernames are "

    for name in username:
        maxPages.append(getMaxPage(name))
    
    pageLists = [] #list of lists containing the complete list of all usernames pages
    for num in maxPages:
        pageLists.append(createList(num))
    
    while(len(overlap) < 1 and bool(any(pageLists))):
        for i in range(len(pageLists)):
            if bool(pageLists[i]):
                pageLists[i], allMovs = getPageMovies(username[i], pageLists[i], allMovs)
        overlap = [item for item, count in collections.Counter(allMovs).items() if count >= len(username)]


    if (len(overlap) > 0):
        randMovie += random.choice(overlap)
    else:
        randMovie += "the users have no overlapping movies in their watchlists"

    overlap.clear()
    maxPages.clear() 
    allMovs.clear()
    return randMovie

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

        resp = MessagingResponse()
        msg = resp.message(result)
        if len(getImage(result)) > 0:
            msg.media(getImage(result))
        end = time.time()
        print(f"sent result was {result} in {end - start} seconds")

    return str(resp)  

@app.route('/test')
def index():
    return "work!!!" 

@app.route('/fail')
def fail():
    resp = MessagingResponse()
    msg = resp.message("there is too much traffic. We recommend limiting the number of usernames you send in if you sent more than two or if a user has a watchlist that is more than 40 pages long.")
    print("fail") 
    return str(resp)  

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/friends', methods=['POST'])
def friends():
    username = request.form['username']
    friends = getFriends(username)[2]
    return render_template('friends.html', myFriends=friends, username=username)

@app.route('/movie', methods=['GET', 'POST'])
def movie():
    userFriends = request.form.getlist('friend')
    print(userFriends)
    movie = getMovie(userFriends)
    source = getImage(movie)
    return render_template('movie.html', movie=movie, link = source)

if __name__ == "__main__":
    app.run(host='0.0.0.0')


