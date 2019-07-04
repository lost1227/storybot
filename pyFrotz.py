import time
import subprocess
from os.path import exists, dirname, join

from abc import ABC, abstractmethod

class GameInterface(ABC):
    
    def __init__(self, game_loc, savegame):
        self.loc = game_loc
        self.savegame = savegame

    @abstractmethod
    def get_intro(self, frotz):
        pass

    def get_loc(self):
        return self.loc
    
    def get_savegame(self):
        return self.savegame
    

class Frotz(object):
    def __init__(self, game_data,
                 interpreter=join(dirname(dirname(__file__)), 'frotz/dfrotz'),
                 opts=[],
                 save_file='save.qzl',
                 prompt_symbol="> >",
                 reformat_spacing=True):
        self.data = game_data
        self.interpreter = interpreter
        self.opts = opts
        self.save_file = save_file
        self.prompt_symbol = prompt_symbol
        self.reformat_spacing = reformat_spacing
        self._get_frotz()

    def _get_frotz(self):

        self.frotz = subprocess.Popen([self.interpreter] + self.opts + [self.data.get_loc()],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE)
        time.sleep(0.1)  # Allow to load

        # Load default savegame
        if exists(self.save_file):
            print('Loading saved game')
            self.restore(self.save_file)

    def save(self, filename=None):
        """
            Save game state.
        """
        filename = filename or self.save_file
        self._frotz_write('save')
        self._clear_until_prompt(':')
        self._frotz_write(filename)  # Accept default savegame
        # Check if game returns Ok or query to overwrite
        while True:
            char = self.frotz.stdout.read(1)
            if char == b'.':  # Ok. (everything is done)
                break  # The save is complete
            if char == b'?':  # Indicates an overwrite query
                self._frotz_write('y')  # reply yes

        self._clear_until_prompt()

    def restore(self, filename=None):
        """
            Restore saved game.
        """
        filename = filename or self.save_file
        self._frotz_write('restore')
        self._clear_until_prompt(':')
        self._frotz_write(filename)  # Accept default savegame
        self._clear_until_prompt()

    def _clear_until_prompt(self, prompt=None):
        """ Clear all received characters until the standard prompt. """
        # Clear all data with title etcetera
        prompt = prompt or self.prompt_symbol
        length = len(prompt)
        lastread = ""
        while not lastread.endswith(prompt):
            if len(lastread) >= length:
                lastread = lastread[1:]
            lastread += self.frotz.stdout.read(1).decode()
        

    def do_command(self, action):
        """ Write a command to the interpreter. """
        self._frotz_write(action)
        return self._frotz_read()

    def _frotz_write(self, data):
        self.frotz.stdin.write(data.encode() + b'\n')
        self.frotz.stdin.flush()

    def _frotz_read(self, parse_room=True, stop_at=['> >','\n)',')    >']):
        """
            Read from frotz interpreter process.
            Returns tuple with Room name and description.
        """
        # Read room info
        output = ""
        output += self.frotz.stdout.read(1).decode()
        if not len(output):
            return ""
        while all(not output.endswith(suffix) for suffix in stop_at):
            output += self.frotz.stdout.read(1).decode()
        for stop in stop_at:
            if output.endswith(stop):
                output = output[:-len(stop)]
        lines = [l.strip() for l in output.split("\n") if l.strip() and "Score: " not in l]
        if parse_room:
            room = lines[0]
            lines = lines[1:]
        lines = ['' if line == '.' else line for line in lines]
        # reformat text by . instead of \n
        if self.reformat_spacing:
            lines = " ".join(lines).replace(" . ", "\n") 
        else:
            lines = "\n".join(lines)
        # Return description removing the prompt
        if parse_room:
            return room, lines
        return lines

    def get_intro(self):
        return self.data.get_intro(self)

    def play_loop(self):
        #print(self.get_intro())
        try:
            while not self.game_ended():
                room, descript = self.do_command(input(">>"))
                print(room)
                print(descript)
        except KeyboardInterrupt:
            pass

    def game_ended(self):
        poll = self.frotz.poll()
        if poll is None:
            return False
        else:
            return True
