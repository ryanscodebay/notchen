import os
import slack
import logging
import ssl as ssl_lib
import hmac
import hashlib
import base64
import time
#import certifi
from flask import Flask, make_response, request, Response
from celery import Celery
from dotenv import load_dotenv

from onboarding import OnboardingTutorial
import mention_response
#import son
#import bot #only if I decide I want this garbo

load_dotenv()
app = Flask(__name__)

#env variables
#SLACK_WEBHOOK_SECRET = os.environ.get('SLACK_WEBHOOK_SECRET')
botTok = os.getenv("BOT_TOK")
legacyToken = os.getenv("LEGACY_TOK")
oAuthTok = os.getenv("OAUTH_TOK")
slack_signing_secret = os.getenv("SLACK_SIGNING_SECRET")

web_client = slack.WebClient(token=botTok)

#basic structures
onboarding_tutorials_sent = {}
{"channel": {"user_id": OnboardingTutorial}}

#basic onboarding
def start_onboarding(web_client: web_client, user_id: str, channel: str):
    # Create a new onboarding tutorial.
    onboarding_tutorial = OnboardingTutorial(channel)

    # Get the onboarding message payload
    message = onboarding_tutorial.get_message_payload()

    # Post the onboarding message in Slack
    response = web_client.chat_postMessage(**message)

    # Capture the timestamp of the message we've just posted so
    # we can use it to update the message after a user
    # has completed an onboarding task.
    onboarding_tutorial.timestamp = response["ts"]

    # Store the message sent in onboarding_tutorials_sent
    if channel not in onboarding_tutorials_sent:
        onboarding_tutorials_sent[channel] = {}
    onboarding_tutorials_sent[channel][user_id] = onboarding_tutorial

#baby's first event handling
#@celery.task
def _event_handler(event_type, slack_event):
  """
  strange internet src: https://github.com/slackapi/Slack-Python-Onboarding-Tutorial/blob/master/app.py 
  A helper function that routes events from Slack to our Bot
  by event type and subtype.
  Parameters
  ----------
  event_type : str
    type of event received from Slack
  slack_event : dict
    JSON response from a Slack reaction event
  Returns
  ----------
  obj
    Response object with 200 - ok or 500 - No Event Handler error
  """
  team_id = slack_event["team_id"]
  # ================ Team Join Events =============== #
  # When the user first joins a team, the type of event will be team_join
  if event_type == "team_join":
    channel_id = slack_event["event"]["channel"]
    user_id = slack_event["event"]["user"]["id"]
    # Send the onboarding message
    start_onboarding(web_client,user_id,channel_id) 
    return make_response("Welcome Message Sent", 200,)

  # ============== Share Message Events ============= #
  # If the user has shared the onboarding message, the event type will be
  # message. We'll also need to check that this is a message that has been
  # shared by looking into the attachments for "is_shared".
  elif event_type == "message" and slack_event["event"].get("attachments"):
    user_id = slack_event["event"].get("user")
    if slack_event["event"]["attachments"][0].get("is_share"):
      # Update the onboarding message and check off "Share this Message"
      #pyBot.update_share(team_id, user_id)
      return make_response("Welcome message updates with shared message",
                           200,)
    return make_response("can't share", 200, {"X-Slack-No-Retry": 1})

  # ============= Reaction Added Events ============= #
  # If the user has added an emoji reaction to the onboarding message
  elif event_type == "reaction_added":
    user_id = slack_event["event"]["user"]
    # Update the onboarding message
    #pyBot.update_emoji(team_id, user_id)
    return make_response("Welcome message updates with reactji", 200,)

  # =============== Pin Added Events ================ #
  # If the user has added an emoji reaction to the onboarding message
  elif event_type == "pin_added":
    user_id = slack_event["event"]["user"]
    # Update the onboarding message
    #pyBot.update_pin(team_id, user_id)
    return make_response("Welcome message updates with pin", 200,)

  #TODO: message events
#  elif event_type == "message":
#    user_id = slack_event["event"]["user"]
#    channel_id = slack_event["event"]["channel"]
#    text = slack_event["event"]["text"]
#    if text and text.lower() == "start":
#      return start_onboarding(web_client, user_id, channel_id)

  elif event_type == "app_mention":
#    user_id = slack_event["event"]["user"]
#    channel_id = slack_event["event"]["channel"]
#    message = "Leave me alone <@" + user_id + "> ;-;"
#    web_client.chat_postMessage(channel=channel_id,text=message,as_user='true')
    
#    slack_client.api_call(
#      "chat.postMessage",
#      channel=channel_id,
#      text=message,
#      username='notchen',
#      icon_url='./avatars/squellie.jpg'
#    # icon_emoji=':robot_face:'
#    )
    #return make_response(message,200,)
    mention_response.contact(web_client,slack_event)
    return make_response('mention',200,)

  # ============= Event Type Not Found! ============= #
  # If the event_type does not have a handler
  message = "You have not added an event handler for the %s" % event_type
  # Return a helpful error message
  return make_response(message, 200, {"X-Slack-No-Retry": 1})

# HTTP interactions
@app.route('/listening', methods=['GET','POST'])
# Thank you strange internet man
def hears():
  slack_event = request.get_json()
  #print(slack_event)
  request_body = request.get_data()
  req_ts = request.headers.get('X-Slack-Request-Timestamp')
  sig_str = str.encode('v0:' + req_ts + ':') + request_body 
  my_signature = 'v0=' + hmac.new(str.encode(slack_signing_secret), sig_str, hashlib.sha256).hexdigest()
  slack_signature = request.headers.get('X-Slack-Signature')

  if abs(time.time() - int(req_ts)) > 120:
    print('timing attack?')
    #minimal guard against timing attacks, 2 minute window
    return make_response("Stop it?",404)
  if not hmac.compare_digest(my_signature, slack_signature):
    print('digests don\'t match >:(')
    #not from slack
    return make_response("Stop it.",404)

  #for json info
  #print(slack_event)
  if "challenge" in slack_event:
    return make_response(slack_event["challenge"], 200, {"content_type": "application/json"})

  # ====== Process Incoming Events from Slack ======= #
  # If the incoming request is an Event we've subscribed to
  if "event" in slack_event:
    event_type = slack_event["event"]["type"]
    # Then handle the event by event_type and have your bot respond
    #_event_handler.delay(event_type, slack_event)
    #return make_response('Event received',200,)
    return _event_handler(event_type, slack_event)
  # If our bot hears things that are not events we've subscribed to,
  # send a quirky but helpful error response
  return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                       you're looking for.", 404, {"X-Slack-No-Retry": 1})

#may use this as actual route in future
#@app.route('/slack', methods=['POST'])
def summoned():
  #are you listening?
  print(request.get_json())

#def inbound():
#  if request.form.get('token') == SLACK_WEBHOOK_SECRET:
#    channel = request.form.get('channel_name')
#    username = request.form.get('user_name')
#    text = request.form.get('text')
#    inbound_message = username + " in " + channel + " says: " + text
#    print(inbound_message)
#  return Response(), 200

#@app.route('/', methods=['GET'])
#def test():
#  return Response('It works!')

# Channel helpers
def list_channels():
  channels_call = slack_client.api_call("channels.list")
  if channels_call['ok']:
    return channels_call['channels']
  return None

def channel_info(channel_id):
  channel_info = slack_client.api_call("channels.info", channel=channel_id)
  if channel_info:
    return channel_info['channel']
  return None

def send_message(channel_id, message):
  slack_client.api_call(
    "chat.postMessage",
    channel=channel_id,
    text=message,
    username='notchen'
#    icon_emoji=':robot_face:'
  )

if __name__ == '__main__':
  app.run(host='10.10.10.93',port=42069,debug=True)
#  app.run(host='127.0.0.1',port=5000,debug=True)
#  ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
#  channel testing
#  channels = list_channels()
#  if channels:
#    print("Channels: ")
#    for c in channels:
#      print(c['name'] + " (" + c['id'] + ")")
#      last_msg = channel_info(c['id'])
#      if last_msg:
#        try:
#          print(last_msg['latest']['text'] + "\n")
#        except:
#          print("Cannot get message, you probably aren't part of the channel\n")
#      if c['name'] == 'general':
#        send_message(c['id'], "Suh bishes. Beep boop :robot_face:")
#  else:
#      print("Unable to authenticate.")
