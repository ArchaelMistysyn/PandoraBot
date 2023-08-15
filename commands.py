import random


# text commands
def get_response(message: str) -> str:
    p_message = message.lower()

    if p_message == 'status':
        return 'Im running cutie'

    if p_message == 'random':
        return str(random.randint(1,100))

    if p_message == '!help':
        return '`Horny are we?`'
