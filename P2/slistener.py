from tweepy import StreamListener
import json, time, sys, random

class SListener(StreamListener):

	def __init__(self, api = None, fprefix = 'streamer'):
		self.api = api or API()
		self.counter = 0
		self.fprefix = fprefix
		self.output  = open(fprefix + '.' + time.strftime('%Y%m%d-%H%M%S') + '.json', 'w')
		self.delout  = open('delete.txt', 'a')
		
		self.unityId = "jjiang13"
		self.myMode = "Loud"

		self.myCheckInStatus = ""
		self.myLocation = ""
		self.myCheckInId = ""
		self.expectedMode = "Loud"
		self.noiseLevel = 0
		self.modeVotes = [0, 0]		# [loud, silent]

		self.myCallStatus = ""
		self.myCallId = ""

		self.myAnswerStatuses = []
		self.myAnswerStatusesIds = []

		self.neighborsResponsesToCheckIn = []
		self.neighborsResponsesToCall = []
		self.neighbors1 = []	# The user id_str's of people who have responded to my check-in messages
		self.neighbors2 = []	# The user id_str's of people who post check-in messages at the same location after I checked in
		self.botNeighbors = []	# The names of bots that are at myLocation

		self.noiseFeedback = [-0.2, -0.1, 0, 0.1, 0.2]
		self.modeFeedback = 0.1

		self.bots = {'Anakin':['family',0], 'Chewbacca':['friend',0], 'Han':['friend',1],
			     'Jango':['stringer',0], 'Jarjar':['friend',2], 'Leia':['family',1],
			     'Mace':['colleague',0], 'ObiWan':['colleague',1], 'Padme':['family',2],
			     'Yoda':['colleague',2]}

	def on_data(self, data):
		if  'in_reply_to_status' in data:
			self.on_status(data)
		elif 'delete' in data:
			delete = json.loads(data)['delete']['status']
			if self.on_delete(delete['id'], delete['user_id']) is False:
				return False
		elif 'limit' in data:
			if self.on_limit(json.loads(data)['limit']['track']) is False:
				return False
		elif 'warning' in data:
			warning = json.loads(data)['warnings']
			print warning['message']
			return false

	def on_status(self, status):
		self.output.write(status + "\n")
		statusJson = json.loads(status)
		statusHashes = json.loads(status)['entities']['hashtags']
		
		# If the status is a response to my check-in message,
		# save the status and add the person to neighbors1
		if (self.myCheckInStatus != ""):
			if statusJson['in_reply_to_status_id_str'] == self.myCheckInId:
				textSplit = statusJson['text'].split("\n")
				if "NOISE" in textSplit[2]:
					self.noiseLevel = int(textSplit[2][textSplit[2].index(':')+2])
					self.neighborsResponsesToCheckIn.append(status)
					self.neighbors1.append(statusJson['user']['id_str'])
					print "The location replied to my check-in:"
					print statusJson['text']
				elif "EXPECTED_MODE" in textSplit[2]:
					if "Name" in textSplit[0]:
						name = textSplit[0][textSplit[0].index(':')+2:]
						if name in self.bots:
							self.botNeighbors.append(name)
					if "Silent" in textSplit[2]:
						self.modeVotes[1] += 1
					elif "Loud" in textSplit[2]:
						self.modeVotes[0] += 1
					print "A neighbor replied to my check-in:"
					print statusJson['text']

		# If the status is a response to my call-request message,
		# i.e. someone calls me,
		# 1. save the status,
		# 2. calculate the utility
		# 3. reply to the call-request message
		if (self.myCallStatus != ""):
			if statusJson['in_reply_to_status_id_str'] == self.myCallId:
				self.neighborsResponsesToCall.append(status)
				# Process the status text
				textSplit = statusJson['text'].split("\n")
				botName = ""
				urgent = 1
				if "Call from" in textSplit[1]:
					botName = textSplit[1][textSplit[1].index(':')+2:]
				if "URGENCY" in textSplit[2]:
					if "0" in textSplit[2]:
						urgent = 0
				print "A Call is received:"
				print statusJson['text']

				# Calculate the utility
				utility = 0.5
				if urgent == 1: utility = 1.0
				else:
					if self.myLocation == "hunt": utility = 0.0
					else:
						utility += noiseFeedback[self.noiseLevel-1]
						if self.modeVotes[0] > self.modeVotes[1]:
							utility += modeFeedback
						else: utility -= modeFeedback
						# The relationship between the caller and the user
						if self.bots[botName][0] != 'stranger':
							if self.bots[botName][1] == 1:
								utility += 0.1
							elif self.bots[botName][1] == 2:
								utility += 0.2
						else:
							utility -= 0.2
						# The relationship between the neighbors and the user
						for bot in self.botNeighbors:
							if self.bots[bot][0] == 'colleague':
								if self.bots[bot][1] == 1:
									utility -= 0.1
								elif self.bots[bot][1] == 1:
									utility -= 0.2
							elif self.bogs[bot][0] == 'stranger':
								utility += 0.1
				print "utility =", utility
				r = random.random()
				# Update my mode and reply to the calls
				if (r < utility) and (utility >= 0):
					self.myMode = "Loud"
					text = '@' + statusJson['user']['screen_name']
					text += "\nAction: Yes"
					text = text + "\n#" + self.unityId + "_" + statusHashes[1]['text'][statusHashes[1]['text'].rfind('_'):]
					text = text + "\n#P2CSC555F15"
					self.api.update_status(status=text, in_reply_to_status_id=statusJson['id'])
					print "CALL-ANSWER REPLY:"
					print text
				else:
					self.myMode = "Silent"
					text = '@' + statusJson['user']['screen_name']
					text += "\nAction: No"
					text = text + "\n#" + self.unityId + "_" + statusHashes[1]['text'][statusHashes[1]['text'].rfind('_'):]
					text = text + "\n#P2CSC555F15"
					self.api.update_status(status=text, in_reply_to_status_id=statusJson['id'])

					print "CALL-ANSWER REPLY:"
					print text

		# If the status is a reply to my call-answer replies:
		if (len(self.myAnswerStatusesIds) > 0):
			if statusJson['in_reply_to_status_id_str'] in self.myAnswerStatusesIds:
				factor = 1
				for answerStatus in self.myAnswerStatuses:
					if (json.loads(answerStatus)['id_str'] == statusJson['in_reply_to_status_id_str']):
						if "NO" in statusJson['text']:
							factor = -1
				if "Positive" in statusJson['text']:
					x = self.noiseFeedback[self.noiseLevel-1]
					self.noiseFeedback[self.noiseLevel-1] = x + abs(x) * 0.1 * factor
					x = self.modeFeedback
					if self.expectedMode == "Loud":
						self.modeFeedback = x + x * 0.1 * factor
					else:
						self.modeFeedback = x - x * 0.1 * factor
				elif "Negative" in statusJson['text']:
					x = self.noiseFeedback[self.noiseLevel-1]
					self.noiseFeedback[self.noiseLevel-1] = x - abs(x) * 0.1 * factor
					x = self.modeFeedback
					if self.expectedMode == "Loud":
						self.modeFeedback = x - x * 0.1 * factor
					else:
						self.modeFeedback = x + x * 0.1 * factor


		# If the status is a check-in message:
		if ('I checked in' in statusJson['text']) and (len(statusHashes) == 3) and (statusHashes[2]['text'] == 'P2CSC555F15'):
			# If the status is mine, reset relevant information
			if (statusJson['user']['id_str'] == '4182757833'):
				self.myCheckInStatus = status
				self.myCheckInId = statusJson['id_str']
				self.myLocation = statusHashes[0]['text']
				if (self.myLocation == "hunt") or (self.myLocation == "eb2"):
					self.expectedMode = "Silent"
				self.neighborsResponsesToCheckIn = []
				self.neighbors1 = []
				self.neighbors2 = []
				self.modeVotes = [0, 0]
				self.botNeighbors = []

				print "My check-in message is received"
			else:
				# If the status is not mine and he/she checked in at myLocation,
				# respond to his/her check-in message.
				if statusHashes[0]['text'] == self.myLocation:
					self.neighbors2.append(statusJson['user']['id_str'])
					text = '@' + statusJson['user']['screen_name']
					text = text + "\nName: " + self.unityId
					text = text + "\nMy_MODE: " + self.myMode
					text = text + "\nEXPECTED_MODE: " + self.expectedMode
					text = text + "\n#" + self.unityId + "_" + statusHashes[1]['text'][statusHashes[1]['text'].rfind('_'):]
					text = text + "\n#P2CSC555F15"
					self.api.update_status(status=text, in_reply_to_status_id=statusJson['id'])
					
					print "Respond to Neighbor's Check-in Message:"
					print text

				# If the check-in message is from my neighbor, delete him/her from my neighbor list
				elif statusJson['user']['id_str'] in self.neighbors1:
					self.neighbors1.remove(statusJson['user']['id_str'])
				elif statusJson['user']['id_str'] in self.neighbors2:
					self.neighbors2.remove(statusJson['user']['id_str'])

		# Else if the status is a call-request message:
		elif ('CALL' in statusJson['text']) and (len(statusHashes) == 2) and (statusHashes[1]['text'] == 'P2CSC555F15'):
			# If the status is mine, update relevant information
			if (statusJson['user']['id_str'] == '4182757833'):
				self.myCallStatus = status
				self.myCallId = statusJson['id_str']
				print "CALL-REQUEST Message is Posted"
		# Else if the status is a call-answer message:
		elif ('ACTION' in statusJson['text']) and (len(statusHashes) == 2) and (statusHashes[1]['text'] == 'P2CSC555F15'):
			# If the status is mine, save it
			if (statusJson['user']['id_str'] == '4182757833'):
				self.myAnswerStatuses.append(status)
				self.myAnswerStatusesIds.append(statusJson['id_str'])
			# If the status is my neighbors', give it feedback.
			elif (statusJson['user']['id_str'] in self.neighbors1) or (statusJson['user']['id_str'] in self.neighbors2):
				response = "Neutral"
				if "YES" in statusJson['text']:
					if (self.expectedMode == "Silent") or (self.noiseLevel < 3):
						response = "Negative"
				else:
					if (self.myLocation == "party") or (self.myLocation == "hunt"):
						response = "Positive"
				text = '@' + statusJson['user']['screen_name']
				text += '\nName: jjiang13_ncsu'
				text += '\nResponse: ' + response
				text += "\n#" + self.unityId + "_" + statusHashes[1]['text'][statusHashes[1]['text'].rfind('_'):]
				text +="\n#P2CSC555F15"

				print "Give Neighbor Feedback:"
				print text
			
		self.counter += 1
		if self.counter >= 20000:
			self.output.close()
			self.output = open('../streaming_data/' + self.fprefix + '.' + time.strftime('%Y%m%d-%H%M%S') + '.json', 'w')
			self.counter = 0
		return

	def on_delete(self, status_id, user_id):
		self.delout.write( str(status_id) + "\n")
		return
	def on_limit(self, track):
		sys.stderr.write(track + "\n")
		return
	def on_error(self, status_code):
		sys.stderr.write('Error: ' + str(status_code) + "\n")
		return False

	def on_timeout(self):
		sys.stderr.write("Timeout, sleeping for 60 seconds...\n")
		time.sleep(60)
		return 
