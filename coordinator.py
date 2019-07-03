import slack
import pyFrotz
import games
from time import sleep

class Coordinator:
    def __init__(self, client):
        self.state = 'standby'
        self.client = client
        self.game = None

    def start_game(self):
        self.game = games.Anchor('stories/anchor.z8')
        self.frotz = pyFrotz.Frotz(self.game, './dfrotz', ['-m','-Z','0','-p','-w','80'], reformat_spacing=False)

    def format_room_message(self, room, description):
        return [
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "plain_text",
                            "text": room.strip()
                        }
                    ]
                }, {
                    "type": "divider"
                }, {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": description.strip()
                    }
                }
        ]
    
    def respond_msg(self, msg):
        text = msg['text']
        channel = msg['channel']
        if self.state == 'standby':
            self.state = 'confirm_start_game'
            self.client.chat_postMessage(
                channel=channel,
                text='Would you like to hear Anchorhead?'
            )
        elif self.state == 'confirm_start_game':
            if 'yes' in text.lower():
                self.state = 'in_game'
                self.start_game()
                intro = self.frotz.get_intro()
                room, description = self.frotz.do_command('look')

                intro = intro.split('\n\n')
                for part in intro:
                    self.client.chat_postMessage(
                        channel=channel,
                        text=part
                    )
                self.client.chat_postMessage(
                    channel = channel,
                    blocks=self.format_room_message(room, description)
                )
            else:
                self.state = 'standby'
                self.client.chat_postMessage(
                    channel=channel,
                    text='Alright, I\'ll save that story for another time'
                )
        elif self.state == 'in_game':
            room, description = self.frotz.do_command(text)
            print("command: "+text+"\n"+"result: "+description)
            self.client.chat_postMessage(
                channel=channel,
                blocks=self.format_room_message(room, description)
            )
