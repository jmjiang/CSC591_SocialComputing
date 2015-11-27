import threading
import time, tweepy, sys

consumer_key = 'T8iXzIqXPsUoHXM9GOZf74oyP'
consumer_secret = 'XbqkAYUl48on9KBFB9Cl7pAv3lmXqXtDfJTHCKZKJVMCMvAEWF'
access_token = '4182757833-o1TV8dHbZu9u0xNQtj3BmpBiHC7NMq4zQGDYLMR'
access_token_secret = 'SjPXNKKipYFz16CgjUFM1KQVY8jmEt1H3PG42sgeFYqqL'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

def checkIn():
	unityID = "jjiang13"
	countCheckIn = 1
	countCall = 1
	while True:
		text = input('ENTER a location (hunt, eb2, carmichael, oval, party) or "call": ')
		if text == "call":
			text = "CALL #" + unityID + "_" + str(countCall) + " #P2CSC555F15"
			countCall += 1
		else:
			text = "I checked in #" + text + " #" + unityID + "_" + str(countCheckIn) + " #P2CSC555F15"
			countCheckIn += 1
		print('POSTED MESSAGE: ', text)
		api.update_status(text)

if __name__ == '__main__':
	checkIn()
