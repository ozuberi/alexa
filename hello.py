##############################
# Builders
##############################
import sys
import json
from flask import Flask, render_template
from flask_ask import Ask, statement, request, question, session, delegate, context


app = Flask(__name__)
ask = Ask(app, "/")

# gets credentials from the person using the skill, should give us their postal code among other things
def getCredentials():
    DEVID = context.System.device.deviceId
    if DEVID != "":
        URL = "https://api.amazonalexa.com/v1/devices/{}/settings/address/countryAndPostalCode".format(context.System.device.deviceId)
    else:
        return statement("no device ID found")
    TOKEN = context.System.apiAccessToken
    if TOKEN != "":
        HEADER = {'Accept': 'application/json','Authorization': 'Bearer {}'.format(TOKEN)}
    else:
        return statement("no token found")

    r = request.get(URL, headers=HEADER)
    if r.status_code == 200:
        return r.json()
		#Need to request permission to access location
    elif r.status_code == 403:
        return statement("403")
    else:
        return question("could not get info")

def addToString(toBeAdded):
    sys.stderr.write(toBeAdded)


def build_PlainSpeech(body):
    speech = {}
    speech['type'] = 'PlainText'
    speech['text'] = body
    return speech


def build_response(message, session_attributes=None):
    if session_attributes is None:
        session_attributes = {}
    response = {}
    response['type'] = 'Dialog.Delegate'
    sys.stderr.write("created response")
    sys.stderr.write(str(response))
    # since we know the order of our questions, we need to get the value
    # in order to print it to our S3 bucket
    if request.intent.slots.value:
        addToString(str(request.intent.slots.value))
    else:
        addToString(str(request.intent.slots))
    return delegate()


def build_SimpleCard(title, body):
    card = {}
    card['type'] = 'Simple'
    card['title'] = title
    card['content'] = body
    return card


##############################
# Responses
##############################


def conversation(title, body, session_attributes):
    speechlet = {}
    speechlet['outputSpeech'] = build_PlainSpeech(body)
    speechlet['card'] = build_SimpleCard(title, body)
    speechlet['shouldEndSession'] = False
    return build_response(speechlet, session_attributes=session_attributes)

def continue_dialog():
    message = {}
    message['shouldEndSession'] = False
    message['directives'] = [{'type': 'Dialog.Delegate'}]
    sys.stderr.write("built message")
    return build_response(message)


##############################
# Custom Intents
##############################

# @ask.intent("TripIntent")
def Surveyintent():
    dialog_state = request.dialogState

    if dialog_state in ("STARTED", "IN_PROGRESS"):
        return continue_dialog()

    # dialog_state == "COMPLETED"
    return statement("Have a good day")


##############################
# Required Intents
##############################


def cancel_intent():
    return statement("You want to cancel")	#don't use CancelIntent as title it causes code reference error during certification

def help_intent():
    return statement("You want help")		#same here don't use CancelIntent

def stop_intent():
    return statement("You want to stop")		#here also don't use StopIntent


##############################
# On Launch
##############################

@ask.launch
def on_launch():
    sys.stderr.write("launched")
    intent_router()


##############################
# Routing
##############################

@ask.intent("SurveyIntent")
def intent_router():
    sys.stderr.write('intent_router activated')
    location = getCredentials()
	#TO DO
	#need to check this if statement to make sure it triggers correctly
	#check to make sure 'statement' is the right way to do it
    if location == statement:
        sys.stderr.write("FAILEDLOCATION SHOULD BE HERE: ")
        sys.stderr.write(str(location))
        return statement("Please allow access to your location").consent_card("read::alexa:device:all:address:country_and_postal_code")
    else:
        sys.stderr.write("LOCATION SHOULD BE HERE: ")
        sys.stderr.write(str(location))
        addToString(str(location["postalCode"]))


    intent = request.intent.name

    if intent == "SurveyIntent":
        sys.stderr.write('Survey intent activated')
        return Surveyintent()
    # Required Intents

    if intent == "AMAZON.CancelIntent":
        return cancel_intent()

    if intent == "AMAZON.HelpIntent":
        return help_intent()

    if intent == "AMAZON.StopIntent":
        return stop_intent()

##############################
# Program Entry
##############################
if __name__ == '__main__':
    sys.stderr.write('__main')
    app.run()
    if request.type == "LaunchRequest":
        sys.stderr.write('launch request')
        on_launch()

    elif request.type == "IntentRequest":
        sys.stderr.write('intent request')
        intent_router()
	# globalString()
