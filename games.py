from pyFrotz import GameInterface

class Anchor(GameInterface):

    def get_intro(self, frotz):
        stdin = frotz.frotz.stdin
        stdout = frotz.frotz.stdout
        frotz._clear_until_prompt(')')
        stdin.write(b'\n')
        stdin.flush()
        intro = frotz._frotz_read(parse_room=False, stop_at=[')','>'])
        stdin.write(b'\n')
        stdin.flush()
        frotz._clear_until_prompt(')')
        stdin.write(b'\n')
        stdin.flush()
        frotz._clear_until_prompt('> >')
        return intro

    def get_loc(self):
        return self.loc
