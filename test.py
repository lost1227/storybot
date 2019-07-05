import pyFrotz
import games

game = games.Anchor('stories/anchor.z8', 'saves', 'anchor')
frotz = pyFrotz.Frotz(game, './dfrotz', ['-m','-Z','0','-p','-w','80'], reformat_spacing=False)

frotz.get_intro()
frotz.do_command('look')
frotz.do_command('go west')
frotz.do_command('go west')
frotz.do_command('go northwest')
frotz.do_command('go west')
print(frotz.do_command('look')[1])
print(game.savegame.get_last_save())
for i in range(5):
    print(game.savegame.list_saves())
    frotz.save(game.savegame.get_next_save())
print(game.savegame.list_saves())
print(game.savegame.get_last_save())
