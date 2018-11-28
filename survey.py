import logging

import requests

import boto3

import json

import sys

from flask import Flask, render_template

from flask_ask import Ask, statement, request, context, question, session, audio, convert_errors


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
		#Need to request permission to access location
	elif r.status_code == 403:
		return statement("403")
	else:
		return question("could not get info")

#Actual Alexa skill back and forth
@ask.launch
def new_survey():
	welcomeMessage = render_template('welcome')
	location = getCredentials()

	#TO DO
	#need to check this if statement to make sure it triggers correctly
	#check to make sure 'statement' is the right way to do it
	if location == statement:
		print("DEBUG", location)
		return statement("Please allow access to your location").consent_card("read::alexa:device:all:address:country_and_postal_code")
	else:
		print("DEBUG", location)
		addToString(str(location["postalCode"]))
		return question(welcomeMessage).simple_card(welcomeMessage)

#They say yes
@ask.intent("AMAZON.YesIntent")
def feel():
	feelingQuestion = render_template('questionTwo')
	addToString("\n" + feelingQuestion)
	return question(feelingQuestion)

# Their answer to our feeling question will be stored in 'feeling'
@ask.intent("answerIntent", mapping={'feeling': 'emotion'})
def answerQ(feeling):
	goodbye = render_template('goodbyeMessage')

	#add user response to question
	addToString(" " + feeling)

	#need to upload our responses at the final question
	createcsv("alexa")
	addCSVToBucket("alexa","alexanielsen")

	return statement("I'm happy you're feeling {}! ".format(feeling) + goodbye)

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
	#NEED TO CHANGE THIS TO REFLECT NEW AWS ACCESS KEY FILE LOCATION
	with open('/Users/osmanzub/Documents/Fellowship/Alexa_Skill/rootkey.json') as f:
		cred = json.load(f)
		#accessing my personal aws security key (written out in a json file in the same directory)
	client = boto3.client(
		's3',
		aws_access_key_id=cred["AccessKeyMetadata"][0]["AccessKeyId"],
		aws_secret_access_key=cred["AccessKeyMetadata"][0]["AWSSecretKey"]
		)
	#now the file will have the name of the device ID-unique for every alexa device
	client.upload_file('alexa', 'alexanielsen', context.System.device.deviceId)

					#___________----------____________

							#END OF UPLOADING

if __name__ == '__main__':
	globalString()
	app.run()
