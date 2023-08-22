import re

import requests
from pypinyin import lazy_pinyin

from my_utils.bot_log import Logger
from global_config import WEATHER_KEY, NO_PROXY
from my_utils.small_func import get_zhishi

botLog=Logger()


GEOAPI_URL="https://geoapi.qweather.com/v2/"
WEATHER_URL="https://devapi.qweather.com/v7/weather/"
WARNING_URL="https://devapi.qweather.com/v7/warning/"

time_pattern=r"\d+-\d+-\d+T(\d+:\d+)"
def get_location(hanStr=None):
    if hanStr==None:
        hanStr="郫都"

    pinyinStr="".join(lazy_pinyin(hanStr))
    params={
        "location": pinyinStr,
        "key": WEATHER_KEY
    }
    url=GEOAPI_URL+f"city/lookup"
    response = requests.get(url, params=params, proxies=NO_PROXY).json()
    if response["code"] == "200":
        return response["location"][0]["id"], response["location"][0]["name"], response["location"][0]["country"]
    else:
        return None

def get_weather_daily(position=None, dayRange=5):
    location = get_location(position)
    if location is None:
        botLog.info("天气模块:daily location error")
        return "day😲似乎定位不到呢"

    url=WEATHER_URL+f"7d"
    params={
        "location": location[0],
        "key": WEATHER_KEY,
    }
    response = requests.get(url, params=params, proxies=NO_PROXY).json()
    # print(response)
    if response.get("code")=="200":
        data=response.get("daily")
        message = f"🌈 {location[2]+'/'+location[1]} {dayRange}天天气预报 🌧️\n-----------------\n"
        for i in range(0,dayRange):
            day = data[i]
            message= message + \
                "{0}:{1}°C~{2}°C {3}(白)/{4}(夜)\n"\
                    .format(day['fxDate'], day['tempMax'], day['tempMin'], day['textDay'], day['textNight'])
        message+=f"-----------------\n" \
                 f"今日日出时间{data[0]['sunrise']}, 日落时间{data[0]['sunset']}\n" \
                 f"月相：{data[0]['moonPhase']},相对湿度:{data[0]['humidity']}"
        return message
    else:
        botLog.info(f"天气模块:daily {response.get('code')} Error")
        return "天气 baozhale..."


def get_weather_hour(position=None, hourRange=6):
    location = get_location(position)
    if location is None:
        botLog.info("天气模块:daily location error")
        return "hour😲似乎定位不到呢"

    hour_url=WEATHER_URL+"24h"
    now_url=WEATHER_URL+"now"
    params={
        "location": location[0],
        "key": WEATHER_KEY,
    }

    now_response = requests.get(url=now_url, params=params, proxies=NO_PROXY).json()
    response = requests.get(hour_url, params=params, proxies=NO_PROXY).json()
    # print(response)

    if response.get("code") == "200" and now_response.get("code") == "200":
        data=response.get("hourly")
        message=f"⏰ {location[2]+'/'+location[1]} {hourRange}小时天气预报 📣\n-----------------\n"
        for i in range(0,hourRange):
            hour=data[i]
            tempTime=re.match(pattern=time_pattern, string=hour["fxTime"]).group(1)

            message += f"{tempTime} {hour['temp']}°C {hour['text']}\n"

        now_data=now_response["now"]

        message += f"-----------------\n" \
                   f"现在天气: {now_data['temp']}°C {now_data['text']}\n" \
                   f"风力{now_data['windScale']}级, 相对湿度{now_data['humidity']}"
        return message
    else:
        botLog.info(f"天气模块:hour{response.get('code')}:{now_response.get('code')} Error")
        return "天气 baozhale..."

def get_weather_warning(position=None):
    location = get_location(position)
    if location is None:
        botLog.info("天气模块:warning location error")
        return None

    url=WARNING_URL+"now"
    params={
        "location": location[0],
        "key": WEATHER_KEY,
        "lang": "zh"
    }
    response = requests.get(url, params=params, proxies=NO_PROXY).json()
    if response.get("code") == "200":
        warn=response["warning"]
        if warn != []:
            return warn[0].get("text")
        else:
            return None

if __name__ == "__main__":
    # print(pinyin.get("看看你的123abc"))
    # print(get_weather_daily())
    print(get_weather_hour())
