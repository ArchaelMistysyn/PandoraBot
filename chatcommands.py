import random
import bosses
import inventory


# text commands
def get_command_text(message: str) -> str:
    p_message = message.lower()

    if p_message == '!status':
        return 'Im running cutie'

    if p_message == 'story1':
        response = '`Fleeing for your life you come across a cave. You\'ve been seperated from your party.'
        response += ' While raiding a possessed fortress your group had been assaulted by a mysterious dragon'
        response += ' You had fought dragons before, but this one was exuding the same dark energies as'
        response += 'the monsters you would find in the fortress. Shrouded in a tainted celestial energy'
        response += 'You know not the cause, but swiftly enter the cave to avoid an untimely fate'
        response += '\nYou are unarmed and know the risks of venturing alone, nevertheless you head deeper.`'
        response += ' The bottom of the cave is oddly well lit, and you approach the source.'
        response += ' You find a floating box, but correct yourself, as you find that it lacks too much form'
        response += ' to be called a box. You lay your hand on the incandescent light as if it was predetermined to be'
        response += ' \nReact ✨ to open the box.'
        return response

    if p_message == '!story2':
        response = "working"
        return response


