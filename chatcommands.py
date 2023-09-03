import random
import bosses
import inventory


# text commands
def get_command_text(message: str) -> str:
    p_message = message.lower()

    if p_message == '!status':
        return 'Im running cutie'

    if p_message == '!story1a':
        response = 'While exorcising a fortress anomaly your party is assaulted by a mysterious dragon.'
        response += ' Shrouded in tainted celestial energy this abnormal creature wiped out over half the group'
        response += ' with a single breath.'
        response += ' Fleeing alone you come across a cave.'
        response += '\n\n You know not why you incurred the dragon\'s wrath, but swiftly enter the cave.'
        response += ' The bottom of the cave is oddly well lit, drawing you in. Pulling you towards the source.'
        response += ' At last you arrive at a strange box radiating all kinds of energies.'
        response += ' The allure is too strong, and you cannot stop yourself from reaching out.'
        response += ' \n\nReact <a:eshadow2:1141653468965257216> to unseal the box.'
        return response

    if p_message == '!story1b':
        response = "A flash floods the room with light and you feel malicious energy escaping all around you. "
        response += "Slowly you refocus your gaze ahead and meet a pair of starry eyes."
        response += '\n\n"Free at last", the voice echoes through your mind.'
        response += ' "Although there sure were a lot of nasty things you just let out of my box.'
        response += ' You will help me get them back. Won\'t you?"'
        response += '\n\nThe girl smiles and nods as if to show you something. '
        response += 'Looking around briefly you see the cave entrance has collapsed, '
        response += 'but a new path now leads deeper. You immediately recognize the '
        response += 'warning signs of an ancient Labyrinth. '
        response += 'Nevertheless there is no choice but to follow her inside.'
        return response

    if p_message == '!quest1':
        response = "Enter the labyrinth with the strange girl.\nUse the '!lab' command"
        return response


