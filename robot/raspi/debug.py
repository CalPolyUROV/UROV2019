PRINTING = True
LOGGING = False

def debug(channel: str, message: str):
    if(PRINTING):
        # Print message to console
        # TODO: Replace all print statements with calls to debug()
        # TODO: Only print if a specific channel is set to be verbose
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