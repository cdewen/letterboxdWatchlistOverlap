# letterboxdWatchlistOverlap

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)

## General info
SMS based application that allows a user to message a phone number a username or list of usernames on the Letterboxd.com website and the app will respond with a random movie that all the usernames texted to the app have in common in their watchlists or a message letting them know there are no overlapping movies.
	
## Technologies
Project is created with:
* Python version: 3.11.1
* Flask version: 2.2.2
* beautifulsoup4 version: 4.11.1
* gunicorn version: 20.1.0
* requests version: 2.27.1
* twilio version: 7.16.1
* ngrok version: 3.1.1
	
## Setup
To run this project, install it locally:

```
$ cd ../letterboxdWatchlistOverlap
$ pip install -r requirements.txt
$ python3 api.py
open a new terminal window
$ ngrok http 5000
```
add the link provided by ngrok as the webhook for a twilio number and now the app is up and running
