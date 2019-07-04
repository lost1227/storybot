import pyFrotz
import games

game = games.Anchor('stories/anchor.z8')
frotz = pyFrotz.Frotz(game, './dfrotz', ['-m','-Z','0','-p','-w','80'], reformat_spacing=False)

frotz.get_intro()
frotz.do_command('look')
frotz.do_command('go west')
frotz.do_command('go west')
frotz.do_command('go northwest')
frotz.do_command('go west')
print(frotz.do_command('look')[1])
frotz.save()

frotz.play_loop()
