from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request 
import os
import tmdbsimple as tmdb
from bs4 import BeautifulSoup
import requests, random
import re
import collections
import time



tmdb.API_KEY = os.environ.get('THE_MOVIE_DB_API_KEY')

movie = tmdb.Movies(603)
response = movie.info()
link = movie.poster_path

movieUrl = "https://image.tmdb.org/t/p/w500" + link

print(movieUrl)




