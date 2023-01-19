import requests
from bs4 import BeautifulSoup
import random

def createUrl(author: str, page: int) -> str:
    url = "https://letterboxd.com/" + author + "/watchlist/" + "page/" + str(page)
    return url

def get_parsed_page(url: str) -> None:
        # This fixes a blocked by cloudflare error i've encountered
        headers = {
            "referer": "https://letterboxd.com",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        return BeautifulSoup(requests.get(url, headers=headers).text, "lxml")
def getWatchlist(username: str) -> list:
    ret = []
    page = [1]
    maxPage: int = 1
    pages = get_parsed_page(createUrl(username, 1))
    pages = pages.find_all("li", {"class":"paginate-page"})

    for item in pages:
        if (item.get_text() == '…'):
            pass
        else: 
            page.append(int(item.get_text()))

    maxPage = max(page)

    i = 1
    while i <= maxPage:
        data = get_parsed_page(createUrl(username, i))
        data = data.find_all("li", {"class":"poster-container"})

        for item in data:
            ret.append(item.find("img", {"class":"image"})['alt'])
        i+=1

    return ret

usernameOne = input('what is the first username? ')
usernameTwo = input('what is the second username? ')

retOne = getWatchlist(usernameOne)
retTwo = getWatchlist(usernameTwo)

set = set(retOne).intersection(set(retTwo))
final = list(set)

randMovie = final[random.randint(0,len(final))]


