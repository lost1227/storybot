from os import listdir
from os.path import isfile, join, getmtime
import re
class Savegames:
    def __init__(self, path, base_name, maxfiles=30):
        self.path = path
        self.basename = base_name
        self.maxfiles = maxfiles

    def list_saves(self):
        """ List all saves, with the most recent first """
        saves = [f for f in listdir(self.path) if isfile(join(self.path, f)) and re.match(r'[0-9]*_'+self.basename, f) is not None]
        saves.sort(key=lambda x: getmtime(join(self.path, x)), reverse=True)
        return saves

    def get_last_save(self):
        saves = self.list_saves()
        if len(saves) <= 0:
            return None
        else:
            return saves[0]

    def get_next_save(self):
        saves = self.list_saves()
        nums = [int(re.match(r"([0-9]*)_", x).group(1)) for x in saves]
        num = 00
        if len(nums) == 0:
            num = 00
        elif len(nums) < self.maxfiles:
            num = max(nums)+1
        else:
            num = nums[-1]
        return join(self.path, '{:02d}_{}.qzl'.format(num, self.basename))
