from slistener import SListener
import threading
import time, tweepy, sys, json

consumer_key = 'T8iXzIqXPsUoHXM9GOZf74oyP'
consumer_secret = 'XbqkAYUl48on9KBFB9Cl7pAv3lmXqXtDfJTHCKZKJVMCMvAEWF'
access_token = '4182757833-o1TV8dHbZu9u0xNQtj3BmpBiHC7NMq4zQGDYLMR'
access_token_secret = 'SjPXNKKipYFz16CgjUFM1KQVY8jmEt1H3PG42sgeFYqqL'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

def checkIn():
	while True:
		x = input('ENTER SOMETHING: ')
		x = x + ' #P2CSC555F15'
		print('You entered ', x)
		api.update_status(x)



def main():
	track = ['#P2CSC555F15']

	listen = SListener(api, 'myprefix')
	stream = tweepy.Stream(auth, listen)

	
	print "Streaming started..."
	try: 
		stream.filter(track = track)
		print "stream: "
	except:
		print "error!"
		stream.disconnect()
	print "DONE"
if __name__ == '__main__':
	main()
