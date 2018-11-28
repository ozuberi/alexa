import logging 

import requests

import boto3

import json

import sys

from flask import Flask, render_template

from flask_ask import Ask, statement, request, context, question, session, audio, convert_errors, delegate


app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger("flask_ask").setLevel(logging.DEBUG)

#I KNOW IT'S BAD STYLE BUT THIS IS TEMPORARY
#Need to add Q1, Q2, etc. everytime user answers a question
#At the end we will upload this to a csv and upload it to a bucket
#Need to initialize it with zipcode so that we can add it right away once we get location
def globalString():
	global personalInfo 
	personalInfo = "ZIPCODE="

#helper function for our dialogue state
def get_dialog_state():
    return request.dialogueState

def continue_dialog():
    message = {}
    message['shouldEndSession'] = False
    message['directives'] = [{'type': 'Dialog.Delegate'}]
    return build_response(message)

#gets credentials from the person using the skill, should give us their postal code among other things
def getCredentials():
	DEVID = context.System.device.deviceId
	if DEVID != "":
		URL =  "https://api.amazonalexa.com/v1/devices/{}/settings/address/countryAndPostalCode".format(context.System.device.deviceId)
	else:
		return statement("no device ID found")
	TOKEN =  context.System.apiAccessToken
	if TOKEN != "":
		HEADER = {'Accept': 'application/json','Authorization': 'Bearer {}'.format(TOKEN)}
	else:
		return statement("no token found")
	r = requests.get(URL, headers=HEADER)
	
	if r.status_code == 200:
		return(r.json())
	elif r.status_code == 403:
		return statement("403")
	else:
		return question("could not get info")


def BeerIntent(self, data):
	dialog_state = self.get_alexa_dialog_state(data)
	self.log(dialog_state)
	if dialog_state == "STARTED":
		return self.format_delegate()
	elif dialog_state == "IN_PROGRESS":
		return self.format_delegate()
	elif dialog_state == "COMPLETED":
		typeOfBeer = self.get_alexa_slot_value(data, slot="typeOfBeer")
		time = self.get_alexa_slot_value(data, slot="times")
		resp = "OK, holding your {} for the next {} minutes".format(type, time)
		return self.format_response(speech=resp, card=resp,title="Beer Situation")


# #Actual Alexa skill back and forth
# @ask.launch
# def new_survey():
# 	welcomeMessage = render_template('welcome')
# 	#location = getCredentials()
# 	#addToString(location["postalCode"])
# 	if get_dialog_state() in ("STARTED", "IN_PROGRESS"):
# 		return continue_dialog()
# 	else:
# 		return statement(welcomeMessage)


# @ask.launch
# def surveyIntent():
# 	dialog_state = get_dialog_state()
# 	if dialog_state in ("STARTED", "IN_PROGRESS"):
# 		return continue_dialog()
# 	elif dialog_state == "COMPLETED":
# 		#call string population function
# 		#need to upload our responses at the final question
# 		addAllQuestions()
# 		createcsv("alexa")
# 		addCSVToBucket("alexa","alexanielsen")
# 	else:
# 		return statement(str(dialog_state))


# 	#request_data = json.loads(request.data)
# 	# if get_dialog_state() != "COMPLETED":
# 	# 	return delegate()
# 	request_data = json.loads(request.data)

# 	if get_dialog_state() != "COMPLETED":
# 		return delegate(request_data['request'])

# 	#return question(welcomeMessage).simple_card(welcomeMessage)

#They say yes
# @ask.intent("surveyIntent")
# def feel():
# 	dialog_state = get_dialog_state()
# 	if dialog_state in ("STARTED", "IN_PROGRESS"):
# 		return continue_dialog()
# 	else:
# 		return statement("error")

# # Their answer to our feeling question will be stored in 'feeling' 
# @ask.intent("surveyIntent")
# def answerQ(feelings):
# 	# write data to database 
# 	# grab info and write back while you still have answer
# 	feelings = updatedIntent.slots.feelings.value

# 	#add user response to question
# 	addToString(" " + feelings)

# 	#request_data = json.loads(request.data)

# 	dialog_state = get_dialog_state()
# 	if dialog_state in ("STARTED", "IN_PROGRESS"):
# 		return continue_dialog()
# 	else:
# 		return statement("error")

# #next question
# @ask.intent("surveyIntent")
# def weatherQ(number):
# 	weatherQuestion = render_template('questionOne')
# 	number = updatedIntent.slots.number.value
# 	addToString("\n" +  str(weatherQuestion)  + str(number))
	
# 	dialog_state = get_dialog_state()
# 	if dialog_state in ("STARTED", "IN_PROGRESS"):
# 		return continue_dialog()
# 	else:
# 		return statement("error")


# @ask.intent("surveyIntent")
# def tvQ(channel):

# 	channelQ = render_template('questionThree')
# 	channel = updatedIntent.slots.channel.value
# 	addToString("\n" + str(channelQ) + str(channel))

# 	goodbyeMessage = render_template('goodbyeMessage')

# 	#need to upload our responses at the final question
# 	createcsv("alexa")
# 	addCSVToBucket("alexa","alexanielsen")

# 	return statement(goodbyeMessage)

								#UPLOADING
					#___________----------____________

#helper function to add to our string
def addToString(toBeAdded):
	global personalInfo
	personalInfo += toBeAdded

#creates file that will be uploaded to S3 bucket
def createcsv(csvFile):
	f = open(csvFile, 'w')
	f.write(personalInfo)
	f.close()

#now we have to take the information and put it somewhere
def addCSVToBucket(csv, bucket):
	with open('C:/Users/zuos8001/Desktop/Alexa/venv/Scripts/rootkey.json') as f:
		cred = json.load(f)
		#accessing my personal aws security key (written out in a json file in the same directory)
	client = boto3.client(
		's3',
		aws_access_key_id=cred["AccessKeyMetadata"][0]["AccessKeyId"],
		aws_secret_access_key=cred["AccessKeyMetadata"][0]["AWSSecretKey"]
		)
	#should potentially be able to replace DEVIDGOESHERE with context.System.device.deviceId
	#no matter the scope
	client.upload_file('alexa', 'alexanielsen', context.System.device.deviceId)

					#___________----------____________
							
							#END OF UPLOADING

if __name__ == '__main__':
	globalString()
	app.run()




