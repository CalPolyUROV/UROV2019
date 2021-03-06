"""Various helper utilities used throughout the code
Attempts to document propper usage of such functions
"""

import os
import sys
import time
from typing import Any, Callable, List, Union

import settings


def print_usage() -> None:
    """Prints a Unix style uasge message on how to start the program
    """
    print("usage: python3 main.py (robot | topside)")


def print_mode(mode: str):
    print("Running as {}".format(mode))


def print_exit(reason: str) -> None:
    """Kills the program after printing the supplied str reason
    """
    sys.stdout.flush()
    sys.stderr.flush()
    print("\nExiting: " + reason.__repr__())
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
    # This point should be unreachable, just die already


def sleep(time_s: Union[int, float]):
    """Pauses the execution of the thread for time_s seconds
    """
    if settings.DISABLE_SLEEP:
        debug("sleep", "Sleep disabled, not sleeping")
        return
    if time_s == 0:
        return

    time.sleep(time_s)


def debug_delay():
    sleep(settings.DEBUGGING_DELAY_S)


def init_dict(keys: List[str], val: Any) -> dict:
    d = {}
    for k in keys:
        d[k] = val
    return d


def attempt(action: Callable[[], bool],
            tries: int, fail_once: Callable,
            failure: Callable[[int], None]) -> None:
    """Wrapper for trying to complete and action with a number of tries
    Should follow this prototype:
    def attmpt_action():
        def try_action() -> bool:
            try:
                return True
            except Exception as error:
                debug("channel", "error: {}", [error.__repr__()])
                return False

        def fail_once() -> None:
            debug("action", "action failed, retrying")
            sleep(settings.ACTION_RETRY_WAIT)

        def failure(tries: int) -> None:
            if settings.REQUIRE_ACTION:
                exit("Could not do required action")
            else:
                debug("action", "Ignoring failing action after {} tries",
                      [tries])
                settings.USE_ACTION = False

        attempt(try_action, settings.ACTION_ATTEMPTS, fail_once, failure)
        debug("action", "Did action")
    """
    attempts = 1
    while (not action()):
        if attempts >= tries:
            failure(attempts)
            return
        fail_once()
        attempts += 1
