import slack
#import flask

def contact(web_client,slack_event):
  user_id = slack_event["event"]["user"]
  channel_id = slack_event["event"]["channel"]
  text = slack_event["event"]["text"]
  message = "Leave me alone <@" + user_id + "> ;-;"

  #start pm
  if "my office" in text:
    new_pm = web_client.im_open(user=user_id)
    message = 'You wanted to see me?' 
    #print (web_client.chat_postMessage(as_user='true',channel=new_pm['channel']['id'],text=greeting))
    channel_id = new_pm['channel']['id']

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
