import time
import random
import threading

from global_config import SELF_ID, TIME_CONFIG, WEATHER_POSITION, AUTH_GROUP
from my_utils import weather, small_func
from base_api import send_message

def weather_clock(hour, minute):
    """
    :param hour:
    :param minute:
    :return:
    """
    if hour == TIME_CONFIG["hour"] and minute == TIME_CONFIG["minute"]:
        for group_id in AUTH_GROUP:
            if TIME_CONFIG["weather"]["enable"]:
                position=WEATHER_POSITION[group_id]
                message = weather.get_weather_daily(position)
                send_message(message, SELF_ID, group_id)

                warning_message=weather.get_weather_warning(position)
                if warning_message is not None:
                    send_message(warning_message, SELF_ID, group_id)
            if TIME_CONFIG["moyu"]["enable"]:
                moyuMessage=small_func.get_moyu_image()
                send_message(moyuMessage, SELF_ID, group_id)

        TIME_CONFIG["enable"]=False

def all_clock():
    """
    持续运行的定时器
    :return: None
    """
    while True:
        now_time = time.localtime()
        hour = now_time.tm_hour
        minute = now_time.tm_min
        if hour == 0 and minute == 0:
            if TIME_CONFIG["enable"]== False:
                TIME_CONFIG["enable"]= True
        if TIME_CONFIG["enable"]:
            weather_clock(hour, minute)

        time.sleep(10)

def run_clock():
    clockThread = threading.Thread(target=all_clock)
    clockThread.daemon = True
    clockThread.start()

if __name__ == "__main__":
    run_clock()
