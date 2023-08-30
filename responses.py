import newbot
import random

EMOJI_LIST = ['😄','😊','🤗']
GOOD_LIST = ['You really think so? 🥺', '😊 I\'m glad you think I\'m a good cake!', 'I\'m really happy to hear that ☺️']
GREET_LIST = ['Hi!', 'Hello!', 'Heyo!', 'Cake!']


def handle_response(message) -> str:
    p_message = message.lower()
    if p_message == 'hi cake' or p_message == 'hello cake':
        return GREET_LIST[random.randint(0, len(GREET_LIST) - 1)] + ' ' + EMOJI_LIST[random.randint(0, len(EMOJI_LIST) - 1)]

    elif p_message == 'cake help':
        return 'Type ' + newbot.COMMAND_PREFIX + 'help to see all my commands!'

    elif p_message == 'good cake':
        return GOOD_LIST[random.randint(0, len(GOOD_LIST) - 1)]
    
    else:
        return ''

def handle_dm(message) ->str:
    p_message = message.lower()
    return 'Hi! 👋 There.'
