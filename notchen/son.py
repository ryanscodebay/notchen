#donut use atm
import os
import slack

from flask import Flask, make_response, request, Response
from onboarding import OnboardingTutorial

botTok = os.getenv("BOT_TOK")
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
      pyBot.update_share(team_id, user_id)
      return make_response("Welcome message updates with shared message",
                           200,)

  # ============= Reaction Added Events ============= #
  # If the user has added an emoji reaction to the onboarding message
  elif event_type == "reaction_added":
    user_id = slack_event["event"]["user"]
    # Update the onboarding message
    pyBot.update_emoji(team_id, user_id)
    return make_response("Welcome message updates with reactji", 200,)

  # =============== Pin Added Events ================ #
  # If the user has added an emoji reaction to the onboarding message
  elif event_type == "pin_added":
    user_id = slack_event["event"]["user"]
    # Update the onboarding message
    pyBot.update_pin(team_id, user_id)
    return make_response("Welcome message updates with pin", 200,)

  #TODO: message events
  elif event_type == "message":
    channel_id = slack_event["event"]["channel"]
    text = slack_event["event"]["text"]
    if text and text.lower() == "start":
      return start_onboarding(web_client, user_id, channel_id)

  elif event_type == "app_mention":
    user_id = slack_event["event"]["user"]
    channel_id = slack_event["event"]["channel"]
    message = "Leave me alone <@" + user_id + "> ;-;"
    web_client.chat_postMessage(channel=channel_id,text=message,as_user='true')

#    slack_client.api_call(
#      "chat.postMessage",
#      channel=channel_id,
#      text=message,
#      username='notchen',
#      icon_url='./avatars/squellie.jpg'
#    # icon_emoji=':robot_face:'
#    )
    #return make_response(message,200,)
    print(make_response(message,200,))

  # ============= Event Type Not Found! ============= #
  # If the event_type does not have a handler
  message = "You have not added an event handler for the %s" % event_type
  # Return a helpful error message
  return make_response(message, 200, {"X-Slack-No-Retry": 1})
