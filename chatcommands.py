import random
import bosses
import inventory


# text commands
def get_response(message: str) -> str:
    p_message = message.lower()

    if p_message == 'status':
        return 'Im running cutie'

    if p_message == '!help':
        return '`Try typing /begin adventure`'

    if p_message == '/begin adventure':
        response = '`Fleeing for your life you come across a cave. You\'ve been seperated from your party.'
        response += ' Out of fear from the creeping darkness you dash into the cave.'
        response += ' You are unarmed and know the fate that soon awaits you, nevertheless you head deeper.`'
        response += ' The bottom of the cave is oddly well lit, and you approach the source.'
        response += ' You find a floating box, but correct yourself, as you find that it lacks too much form'
        response += ' to be called a box. You lay your hand on the incandescent light as if it was predetermined to be'
        response += ' \n Please react :sparkle: to open the box.'
        return response


