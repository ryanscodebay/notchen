import os
import message

from slackclient import SlackClient

authed_teams = {}

class Bot(object):
  """ Instantiates a Bot object to handle Slack onboarding interactions."""
  def __init__(self):
    super(Bot, self).__init__()
    self.name = "NotchenHelperBot"
    self.emoji = ":sure:"
    self.oauth = {"client_id": os.environ.get("CLIENT_ID"),
                  "client_secret": os.environ.get("CLIENT_SECRET"),
                  "scope": "bot"}
    self.verification = os.environ.get("VERIFICATION_TOKEN")

    self.client = SlackClient("")
    self.messages = {}

  def auth(self, code):
    """
    Authenticate with OAuth and assign correct scopes.
    Save a dictionary of authed team information in memory on the bot
    object.

    Parameters
    ----------
    code : str
        temporary authorization code sent by Slack to be exchanged for an
        OAuth token
    """
    # After the user has authorized this app for use in their Slack team,
    # Slack returns a temporary authorization code that we'll exchange for
    # an OAuth token using the oauth.access endpoint
    auth_response = self.client.api_call(
                            "oauth.access",
                            client_id=self.oauth["client_id"],
                            client_secret=self.oauth["client_secret"],
                            code=code
                            )
    # To keep track of authorized teams and their associated OAuth tokens,
    # we will save the team ID and bot tokens to the global
    # authed_teams object
    team_id = auth_response["team_id"]
    authed_teams[team_id] = {"bot_token":
                             auth_response["bot"]["bot_access_token"]}
    # Then we'll reconnect to the Slack Client with the correct team's
    # bot token
    self.client = SlackClient(authed_teams[team_id]["bot_token"])

  def open_dm(self, user_id):
    """
    Open a DM to send a welcome message when a 'team_join' event is
    recieved from Slack.

    Parameters
    ----------
    user_id : str
        id of the Slack user associated with the 'team_join' event

    Returns
    ----------
    dm_id : str
        id of the DM channel opened by this method
    """
    new_dm = self.client.api_call("im.open",
                                  user=user_id)
    dm_id = new_dm["channel"]["id"]
    return dm_id

  def onboarding_message(self, team_id, user_id):
    """
    Create and send an onboarding welcome message to new users. Save the
    time stamp of this message on the message object for updating in the
    future.

    Parameters
    ----------
    team_id : str
        id of the Slack team associated with the incoming event
    user_id : str
        id of the Slack user associated with the incoming event

    """
    if self.messages.get(team_id):
        # Then we'll update the message dictionary with a key for the
        # user id we've received and a value of a new message object
        self.messages[team_id].update({user_id: message.Message()})
    else:
        self.messages[team_id] = {user_id: message.Message()}
    message_obj = self.messages[team_id][user_id]
    message_obj.channel = self.open_dm(user_id)
    message_obj.create_attachments()
    post_message = self.client.api_call("chat.postMessage",
                                        channel=message_obj.channel,
                                        username=self.name,
                                        icon_emoji=self.emoji,
                                        text=message_obj.text,
                                        attachments=message_obj.attachments
                                        )
    timestamp = post_message["ts"]
    message_obj.timestamp = timestamp

  def update_emoji(self, team_id, user_id):
    """
    Update onboarding welcome message after recieving a "reaction_added"
    event from Slack. Update timestamp for welcome message.

    Parameters
    ----------
    team_id : str
        id of the Slack team associated with the incoming event
    user_id : str
        id of the Slack user associated with the incoming event

    """
    completed_attachments = {"text": ":white_check_mark: "
                                     "~*Add an emoji reaction to this "
                                     "message*~ :thinking_face:",
                             "color": "#439FE0"}
    message_obj = self.messages[team_id].get(user_id)
    message_obj.emoji_attachment.update(completed_attachments)
    post_message = self.client.api_call("chat.update",
                                        channel=message_obj.channel,
                                        ts=message_obj.timestamp,
                                        text=message_obj.text,
                                        attachments=message_obj.attachments
                                        )
    message_obj.timestamp = post_message["ts"]

  def update_pin(self, team_id, user_id):
    """
    Update onboarding welcome message after receiving a "pin_added"
    event from Slack. Update timestamp for welcome message.

    Parameters
    ----------
    team_id : str
        id of the Slack team associated with the incoming event
    user_id : str
        id of the Slack user associated with the incoming event

    """
    completed_attachments = {"text": ":white_check_mark: "
                                     "~*Pin this message*~ "
                                     ":round_pushpin:",
                             "color": "#439FE0"}
    message_obj = self.messages[team_id].get(user_id)
    message_obj.pin_attachment.update(completed_attachments)
    post_message = self.client.api_call("chat.update",
                                        channel=message_obj.channel,
                                        ts=message_obj.timestamp,
                                        text=message_obj.text,
                                        attachments=message_obj.attachments
                                        )
    message_obj.timestamp = post_message["ts"]

  def update_share(self, team_id, user_id):
    """
    Update onboarding welcome message after recieving a "message" event
    with an "is_share" attachment from Slack. Update timestamp for
    welcome message.

    Parameters
    ----------
    team_id : str
        id of the Slack team associated with the incoming event
    user_id : str
        id of the Slack user associated with the incoming event

    """
    # These updated attachments use markdown and emoji to mark the
    # onboarding task as complete
    completed_attachments = {"text": ":white_check_mark: "
                                     "~*Share this Message*~ "
                                     ":mailbox_with_mail:",
                             "color": "#439FE0"}
    # Grab the message object we want to update by team id and user id
    message_obj = self.messages[team_id].get(user_id)
    # Update the message's attachments by switching in incomplete
    # attachment with the completed one above.
    message_obj.share_attachment.update(completed_attachments)
    # Update the message in Slack
    post_message = self.client.api_call("chat.update",
                                        channel=message_obj.channel,
                                        ts=message_obj.timestamp,
                                        text=message_obj.text,
                                        attachments=message_obj.attachments
                                        )
    # Update the timestamp saved on the message object
    message_obj.timestamp = post_message["ts"]
