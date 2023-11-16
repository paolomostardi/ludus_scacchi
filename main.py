from FrontEnd import play_mode
from FrontEnd import training_mode



'''color = play_mode.color_choice()

print('----------------- COLOR OF THE PLAYER ---------------')

if color is None:
    print('random color')
if color is True:
    print('white color')
if color is False:
    print('black color')

board, resign = play_mode.main(color)
print(color)

play_mode.ending_message(board, color, resign)
'''


training_mode.main()