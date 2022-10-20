""" Allows for more readable logging of key steps during execution """
import logging

import logging

logging.basicConfig()

logging.root.setLevel(logging.INFO)

logging.basicConfig(level=logging.INFO, filename='logs.txt', format='%(levelname)-.4s:%(asctime)s:%(message)s')
handle = "my-app"
logger = logging.getLogger(handle)
logger2 = logging.getLogger(handle)

import platform
import time
from inspect import getframeinfo, stack
from colorama import Fore, Style


def xlogging(set_debug_level, text_out, log_as_step='n', sleep_secs=0, frame_stack=1):
    """ This allows a specific wait time to be passed when sending a message to the console
    :param log_as_step: default is 'n', use count_step='y' if log should also be counted as a step to be logged to steps file
    :param set_debug_level: 1:DEBUG, 2:INFO, 3:, WARNING, 4:ERROR, 5:CRITICAL
    :param text_out: Message to be printed to the console
    :param sleep_secs: How long to wait before continuing with the program
    :param frame_stack: Set to true if the file calling this function == xpath_tools.py
    :return: Void """

    caller = getframeinfo(stack()[frame_stack][0])

    if platform.system() == 'Windows':
        f_name = caller.filename.split('\\')[-1]
    else:
        f_name = caller.filename.split('/')[-1]

    if set_debug_level == 1:
        debug_level = logging.debug
        log_level = 'Debug: '
        colour = Fore.WHITE
    elif set_debug_level == 2:
        debug_level = logging.info
        log_level = 'Info: '
        colour = Fore.GREEN
    elif set_debug_level == 3:
        debug_level = logging.warning
        log_level = 'Warn: '
        colour = Fore.YELLOW
    elif set_debug_level == 4:
        debug_level = logging.error
        log_level = 'Error: '
        colour = Fore.LIGHTRED_EX
    elif set_debug_level == 5:
        debug_level = logging.critical
        log_level = 'CRITICAL: '
        colour = Fore.RED
    else:
        debug_level = 2
        log_level = ''
        colour = Fore.WHITE

    if log_as_step == 'n':
        if sleep_secs != 0:
            if platform.system() == 'Windows':
                debug_level(f'{f_name:<20}:{caller.lineno:<3}:{colour}{log_level} {text_out}; wait duration: {sleep_secs} second(s){Style.RESET_ALL}')
            else:
                debug_level(f'{f_name:<20}:{caller.lineno:<3}:{log_level} {text_out}; wait duration: {sleep_secs} second(s)')
        else:
            if platform.system() == 'Windows':
                debug_level(f'{f_name:<20}:{caller.lineno:<3}:{colour}{log_level} {text_out}{Style.RESET_ALL}')
            else:
                debug_level(f'{f_name:<20}:{caller.lineno:<3}:{log_level} {text_out}')
        time.sleep(sleep_secs)

    if log_as_step == 'y':
        if sleep_secs != 0:
            if platform.system() == 'Windows':
                debug_level(f'{f_name:<20}:{caller.lineno:<3}:{Fore.LIGHTBLUE_EX}{log_level} {text_out}; wait duration: {sleep_secs} second(s){Style.RESET_ALL}')
            else:
                debug_level(f'{f_name:<20}:{caller.lineno:<3}:{log_level} {text_out}; wait duration: {sleep_secs} second(s)')

        else:
            if platform.system() == 'Windows':
                debug_level(f'{f_name:<20}:{caller.lineno:<3}:{Fore.LIGHTBLUE_EX}{log_level} {text_out}{Style.RESET_ALL}')
            else:
                debug_level(f'{f_name:<20}:{caller.lineno:<3}:{log_level} {text_out}')

        time.sleep(sleep_secs)
