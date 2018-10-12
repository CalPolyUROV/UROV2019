PRINTING = True
LOGGING = False

# Usage:
# debug("channel", "message")
# debug("channel", object)
# debug_f("channel", "message with brackets: {}, {}", ["list", of_things_to_format_in])

# equivelant to (don't do the following):
#     debug("channel", "message with brackets: {}, {}".format("list", of_things_to_format_in)
# By formatting once inside debug_f(), format() is only called if printing is turned on.

channels = {"sockets": True,
            "serial": True,
            "serial_finder": True,
            "execute_task": True}

def debug(channel: str, message: str):
    if(PRINTING & channels[channel]):
        # Print message to console
        # TODO: Replace all print statements with calls to debug()
        print("{}: {}".format(channel, message))
    if(LOGGING):
        # TODO: Output stuff to a log file
        pass

def debug_f(channel: str, message: str, formatting: list):
    if(PRINTING):
        # TODO: Do this better
        print("{}: {}".format(channel, message.format(*formatting)))
    if(LOGGING):
        # TODO: Output stuff to a log file
        pass   