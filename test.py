import pyFrotz
import games

game = games.Anchor('stories/anchor.z8')
frotz = pyFrotz.Frotz(game, './dfrotz', ['-m','-Z','0','-p','-w','80'], reformat_spacing=False)

print(frotz.get_intro())
print(frotz.do_command("look")[1])

frotz.play_loop()
