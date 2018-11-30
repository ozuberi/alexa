# from flask import Flask
#
# from flask_ask import Ask
#
# app = Flask(__name__)
# @app.route('/')
# def hello():
#     return 'Hello\n'
#
# if __name__ == "__main__":
#     app.run()

##############################
# Builders
##############################
import sys
import json
from flask import Flask, render_template
from flask_ask import Ask, statement, request, question, session


app = Flask(__name__)
ask = Ask(app, "/")

def build_PlainSpeech(body):
    speech = {}
    speech['type'] = 'PlainText'
    speech['text'] = body
    return speech


def build_response(message, session_attributes=None):
    if session_attributes is None:
        session_attributes = {}
    response = {}
    response['version'] = '1.0'
    response['sessionAttributes'] = session_attributes
    response['response'] = message
    sys.stderr.write("created response")
    # sys.stderr.write(response)
    return response['response']


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

#
# def statement(title, body):
#     speechlet = {}
#     speechlet['outputSpeech'] = build_PlainSpeech(body)
#     speechlet['card'] = build_SimpleCard(title, body)
#     speechlet['shouldEndSession'] = True
#     return build_response(speechlet)


def continue_dialog():
    message = {}
    message['shouldEndSession'] = False
    message['directives'] = [{'type': 'Dialog.Delegate'}]
    sys.stderr.write("built message")
    return build_response(message)


##############################
# Custom Intents
##############################


# def sing_intent(event, context):
#     song = "Daisy, Daisy. Give me your answer, do. I'm half crazy all for the love of you"
#     return statement("daisy_bell_intent", song)
#
#
# def counter_intent(event, context):
#     """
#     in order to maintain the session , return the session object in every response
#     """
#     if 'attributes' in event['session']:
#         session_attributes = event['session']['attributes']
#         if 'counter' in session_attributes:
#             session_attributes['counter'] += 1
#         else:
#             session_attributes['counter'] = 1
#     else:
#         event['session']['attributes'] = {}
#         session_attributes = event['session']['attributes']
#         if 'counter' not in session_attributes:
#             session_attributes['counter'] = 1
#     return conversation("SessionIntent", session_attributes['counter'], session_attributes)



# @ask.intent("TripIntent")
def trip_intent():
    sys.stderr.write('POOPITY SCOOPITY WOOP WOOP')
    dialog_state = request.dialogState
    sys.stderr.write(dialog_state)


    if dialog_state in ("STARTED", "IN_PROGRESS"):
        return continue_dialog()

    elif dialog_state == "COMPLETED":
        return statement("Have a good trip")

    else:
        return statement("No dialog")


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

@ask.intent("TripIntent")
def intent_router():
    sys.stderr.write('intent_router activated')
    intent = request.intent.name

    # Custom Intents

    # if intent == "CounterIntent":
    #     return counter_intent(event, context)
    #
    # if intent == "SingIntent":
    #     return sing_intent(event, context)

    if intent == "TripIntent":
        sys.stderr.write('trip intent activated')
        return trip_intent()
    else:
        return statement("made it this far")

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
    # def lambda_handler(event, context):
    sys.stderr.write('lambda_handler')
    # something is up with the skill not being able to access the event
    # and the context. Need to check to how to actually pass in event/context
    # and if not try to run the skill without them
    if request.type == "LaunchRequest":
        sys.stderr.write('launch request')
        on_launch()

    elif request.type == "IntentRequest":
        sys.stderr.write('intent request')
        intent_router()
	# globalString()


# def lambda_handler(event, context):
#     if event['request']['type'] == "LaunchRequest":
#         return on_launch(event, context)
#
#     elif event['request']['type'] == "IntentRequest":
#         return intent_router(event, context)
