from coordinator import Coordinator
from slackeventsapi import SlackEventAdapter
import slack
import specificvars
import re
import threading
import queue
from time import sleep

slack_events_adapter = SlackEventAdapter(specificvars.slack_signing_secret, endpoint="/slack/events")
webclient = slack.WebClient(token=specificvars.bot_user_token)
rtmclient = slack.RTMClient(token=specificvars.bot_user_token)

respond_msg_queue = queue.Queue()
output_queue = queue.Queue()

coord = Coordinator(output_queue)

@slack_events_adapter.on("app_mention")
def app_mention(event_data):
    event = event_data['event']
    text = event['text']
    clean_text = re.sub(r'<@.*>', '', text)
    event['text'] = clean_text
    event['dubious'] = False
    respond_msg_queue.put(event)

@slack.RTMClient.run_on(event='message')
def channel_msg(**payload):
    data = payload['data']
    channel = data['channel']
    if 'subtype' in data and data['subtype'] == 'bot_message':
        return
    if re.search(r'<@.*>', data['text']) is not None:
        return
    respond_msg_queue.put(data)

def consume_output_queue(queue):
    """ Gets message objects from queue and sends them
        message objects are of the following form: {"sleep":0, "channel":"", "text":"", "blocks":[]} """
    while True:
        data = queue.get()
        if 'text' in data:
            response = webclient.chat_postMessage(channel=data['channel'], text=data['text'])
        elif 'blocks' in data:
            response = webclient.chat_postMessage(channel=data['channel'], blocks=data['blocks'])
        else:
            raise RuntimeError("Bad output message")
        
        if not response['ok']:
            raise RuntimeError("Slack error: {}".format(response['error']))

        if 'sleep' in data:
            sleep(data['sleep'])

def consume_msg_queue(coord, queue):
    while True:
        msg = queue.get()
        dubious = msg.pop('dubious', True)
        coord.respond_msg(msg, dubious)

flask_thread = threading.Thread(target=slack_events_adapter.start, kwargs={"host":'0.0.0.0', "port":'3000'}, name='flask_thread')
msg_responder_thread = threading.Thread(target=consume_msg_queue, kwargs={'coord':coord, 'queue':respond_msg_queue}, name='msg_responder_thread')
msg_sender_thread = threading.Thread(target=consume_output_queue, kwargs={"queue":output_queue}, name='msg_sender_thread')

flask_thread.daemon = True
msg_responder_thread.daemon = True
msg_sender_thread.daemon = True

flask_thread.start()
msg_responder_thread.start()
msg_sender_thread.start()

rtmclient.start()
