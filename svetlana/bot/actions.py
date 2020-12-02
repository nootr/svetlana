"""
This module contains a set of methods which are used to generate a response.
"""

DESCRIPTION = """I respond to the following commands (friends call me 'svet'):
    * Svetlana hi/help - I'll show you this list!
    * Svetlana follow <ID> - I'll keep track of a game with this ID.
    * Svetlana unfollow <N> - I'll stop following this given game.
    * Svetlana alert <N> - I'll alert N hours before a deadline.
    * Svetlana silence <N> - I won't alert N hours before a deadline.
    * Svetlana list - I'll give you a list of the games I'm following.

I will give a notification when a new round starts and two hours before it
starts and will warn you if players have not given their orders yet.

For more info, check out https://gitlab.jhartog.dev/jhartog/svetlana
"""


def respond_hi(**kwargs):
    """Returns a response to `hi` in the form of a tuple."""
    message = kwargs['message']

    return f'Hello, {message.author.name}!\n{DESCRIPTION}'

def respond_follow(**kwargs):
    """Returns a response to `follow`."""
    arguments = kwargs['arguments']
    bot = kwargs['bot']
    message = kwargs['message']

    game_id = int(arguments[0])
    game = bot.wd_client.fetch(game_id)
    if bot.follow(game_id, message.channel.id):
        desc = f'Now following {game_id}!'
    else:
        desc = "I'm already following that game!"
    msg = bot.get_embed(game, desc)
    return msg

def respond_unfollow(**kwargs):
    """Returns a response to `unfollow`."""
    arguments = kwargs['arguments']
    bot = kwargs['bot']
    message = kwargs['message']

    game_id = int(arguments[0])
    if bot.unfollow(game_id, message.channel.id):
        msg = 'Consider it done!'
    else:
        msg = 'Huh? What game?'
    return msg

def respond_alert(**kwargs):
    """Returns a response to `alert`."""
    arguments = kwargs['arguments']
    bot = kwargs['bot']
    message = kwargs['message']

    if arguments[0] == 'list':
        alarms = [f'T-{h}h' for h, c in bot.alarms if c == message.channel.id]
        msg = "I'm alerting at: " + ', '.join(alarms)
    else:
        hours = int(arguments[0])
        if bot.add_alert(hours, message.channel.id):
            msg = f'OK, I will alert {hours} hours before a deadline.'
        else:
            msg = f"I'm already alerting {hours} hours before a deadline!"
    return msg

def respond_silence(**kwargs):
    """Returns a response to `silence`."""
    arguments = kwargs['arguments']
    bot = kwargs['bot']
    message = kwargs['message']

    hours = int(arguments[0])
    if bot.remove_alert(hours, message.channel.id):
        msg = f'Understood, I will stop alerting T-{hours}h..'
    else:
        msg = f"I already don't alert {hours} hours before a deadline?!"
    return msg

def respond_list(**kwargs):
    """Returns a response to `list`."""
    bot = kwargs['bot']
    message = kwargs['message']

    game_ids = [str(g) for g, c, _ in bot.pollers if c == message.channel.id]
    msg = "I'm following: " + ', '.join(game_ids)
    return msg
