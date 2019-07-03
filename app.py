from coordinator import Coordinator
from slackeventsapi import SlackEventAdapter
import slack
import specificvars
import re

slack_events_adapter = SlackEventAdapter(specificvars.slack_signing_secret, endpoint="/slack/events")
client = slack.WebClient(token=specificvars.bot_user_token)
coord = Coordinator(client)

@slack_events_adapter.on("app_mention")
def app_mention(event_data):
    event = event_data['event']
    text = event['text']
    clean_text = re.sub(r'<@.*>', '', text).strip()
    event['text'] = clean_text
    channel = event['channel']
    user = event['user']
    coord.respond_msg(event)


slack_events_adapter.start(host='0.0.0.0', port='3000', debug=False)
