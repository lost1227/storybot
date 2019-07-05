import slack
import pyFrotz
import games
from time import time
import re
import os.path

class Coordinator:
    def __init__(self, msgqueue):
        self.state = 'standby'
        self.msgqueue = msgqueue
        self.game = games.Anchor('stories/anchor.z8', 'saves', 'anchor')
        self.last_ts = {}
        self.timeout = 1 * 60

    def start_game(self):
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
    
    def respond_msg(self, msg, text_dubious=True):
        text = msg['text'].strip()
        channel = msg['channel']

        accept_dubious = channel in self.last_ts and self.last_ts[channel] is not None and time() - self.last_ts[channel] < self.timeout

        if not self.msgqueue.empty():
            # Ignore user messages until all the information has been given
            return

        if self.state == 'standby':
            if text_dubious:
                return
            self.state = 'confirm_start_game'
            self.msgqueue.put({'channel':channel, 'text':'Would you like to hear Anchorhead?'})
        elif self.state == 'confirm_start_game':
            if 'yes' in text.lower():
                if text_dubious and not accept_dubious:
                    return

                self.state = 'confirm_restore'

                savepath = self.game.savegame.get_last_save()

                if savepath is not None:
                    self.msgqueue.put({'channel':channel, 'text':"Should I continue from where I last stopped?"})
                else:
                    msg['text'] = 'no'
                    self.respond_msg(msg, text_dubious)
            else:
                # timeout the question
                if not accept_dubious:
                    self.state = 'standby'
                # respond if the message is actually for us
                if text_dubious and not accept_dubious:
                    return
                self.state = 'standby'
                self.msgqueue.put({'channel':channel, 'text':'Alright, I\'ll save that story for another time'})
        elif self.state == 'confirm_restore':
            self.state = 'in_game'
            self.start_game()
            intro = self.frotz.get_intro()
            if 'yes' in text.lower():
                self.frotz.restore(self.game.savegame.get_last_save())
            else:
                intro = intro.split('\n\n')
                for part in intro:
                    self.msgqueue.put({'sleep':1+len(part) / 50, 'channel':channel, 'text':part})
            room, description = self.frotz.do_command('look')
            self.msgqueue.put({'channel':channel, 'blocks':self.format_room_message(room, description)})
        elif self.state == 'in_game':
            if text_dubious and not accept_dubious:
                return
            if text.lower().startswith("help") or text.lower().startswith("about"):
                return
            if text.lower().startswith("save"):
                self.frotz.save(self.game.savegame.get_next_save())
                self.msgqueue.put({'channel':channel, 'text':'Story location saved'})
                return
            if text.lower().startswith("restore") or text.lower().startswith("load"):
                self.frotz.restore(self.game.savegame.get_last_save())
                text = 'look'
            if text.lower().startswith("quit"):
                self.state = 'confirm_quit'
                self.msgqueue.put({'channel':channel, 'text':'Would you like me to save our progress?'})
                return
            room, description = self.frotz.do_command(text)
            if text_dubious and description.lower().strip() == "that's not a verb i recognise.":
                self.last_ts[channel] = None
                return
            self.msgqueue.put({'channel':channel, 'blocks':self.format_room_message(room, description)})
        elif self.state == 'confirm_quit':
            self.state = 'standby'
            if 'yes' in text.lower():
                self.frotz.save(self.game.savegame.get_next_save())
            self.frotz.quit_frotz()
            self.msgqueue.put({'channel':channel, 'text':'Story closed, for now'})

        self.last_ts[channel] = time()
