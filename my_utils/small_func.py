import re

import requests
import datetime
import random
from my_utils.cq_code import get_reply, get_group_picture
from my_utils.bot_log import Logger
from base_api import get_regex_group1
from global_config import NO_PROXY

botLog=Logger()

def get_gaokao_message() -> str:
    """
    返回构造的高考倒计时以及高考时的时间。

    :return: str: message
    """
    nowDay = datetime.date.today()
    # nowDay=datetime.date(2023, 12, 25)
    if nowDay.month == 6 and nowDay.day >= 7 and nowDay.day <= 9:
        if nowDay.day == 7:
            return "😱高考第1天！\n上午：\n语文 9：00~11：30\n" \
                   "下午：\n数学 15：00~17：00"
        elif nowDay.day == 8:
            return "😱高考第2天！\n上午：\n物理/历史 9：00~10：15\n" \
                   "下午：\n外语 15：00~17：00"
        else:
            return "😋高考第3天！\n上午：\n化学 8：30~9：45\n" \
                   "地理：11：00~12：15\n下午：\n思想政治 14：30~15：45\n" \
                   "生物：17：00~18：15"

    elif nowDay.month < 6 or (nowDay.month == 6 and nowDay.day < 7):
        year = datetime.date.today().year
    else:
        year = datetime.date.today().year + 1
    gaokaoDay = datetime.date(year, 6, 7)
    num = gaokaoDay - nowDay
    return "距离高考还有 {0} 天！".format(str(num.days))


def get_jrrp_message(message_id,user_id, nickname=""):
    num_id = int(user_id)
    id_date = num_id + int(datetime.date.today().strftime("%y%m%d"))
    random.seed(id_date)
    jrrpResult = random.randint(0,100)
    return "{0}{1} 今日运势 {2}".format(get_reply(message_id), nickname, str(jrrpResult))

def get_moyu_image():
    """
    获取摸鱼人日历
    :return: 消息string
    """

    url = "https://moyu.qqsuu.cn/?type=json"
    try:
        # 重定向导致要再来一个request
        response = requests.get(url=url, proxies=NO_PROXY).json()
        # print(response)
        if response.get("code") == 200:
            moyu_url=response["data"]
            response = requests.get(moyu_url)
            return get_group_picture(response.url)
        else:
            return "🤯摸不了了，开卷！"
    except Exception as e:
        botLog.info(f"摸鱼摸错了！{e}")
        return "🤯摸鱼模块错误！"

def get_anke_message(message:str,message_id:int, rang=100)->str:
    judge= random.randint(0,rang)
    reply = get_reply(message_id)
    return f"{reply}由于{message} 判定结果为{judge}。"

def get_zhishi():
    zhishi = ["雪豹","猞猁","丁真","狐狸","土拨鼠","獐子","岩羊","顶真","电子烟","锐刻","礼堂","理塘"]
    if random.random()>0.5:
        return "芝士"+zhishi[random.randint(0,len(zhishi)-1)]
    else:
        return zhishi[random.randint(0,len(zhishi)-1)]+"闭嘴"

def get_ip_message(message:str, message_id):
    ip = get_regex_group1(pattern=r"\.ip\s+([\w\.]+)", string=message)
    if ip is None:
        return "疑似输入错误🧐"

    reply = get_reply(message_id)
    url = f"http://ip-api.com/json/{ip}?lang=zh-CN"
    response = requests.get(url, proxies=NO_PROXY).json()
    if response.get("status") == "success":
        data = response
        message = reply +\
                  f"---------ip查询结果--------\n" \
                  f"ip address: {ip}\n" \
                  f"country: {data['country']}\n" \
                  f"area: {data['regionName']}\n"\
                  f"ISP: {data['isp']}\n" \
                  f"org: {data['org']}"

        return message
    else:
        botLog.info(f"IP查询出错:code {response.get('code')}")
        return reply + f"IP查询出错:code {response.get('code')}"

def get_tel_message(message:str, message_id):
    tel = get_regex_group1(pattern=r"\.tel\s+(\d+)", string=message)
    if tel is None:
        return "疑似输入错误🧐"

    reply = get_reply(message_id)
    url = f"https://cx.shouji.360.cn/phonearea.php?number={tel}"
    response = requests.get(url=url, proxies=NO_PROXY).json()
    if response.get("code") == 0:
        data = response["data"]
        message = reply + \
                  f"---------手机号查询结果---------\n" \
                  f"{tel}信息如下：\n" \
                  f"sp: {data['sp']}\n" \
                  f"location: {data['province']+data['city']}"
        return message
    else:
        botLog.info(f"手机号查询出错:code {response.get('code')}")
        return reply + f"手机号查询出错:code {response.get('code')}"

def get_earth():
    utc_time = datetime.datetime.now() - datetime.timedelta(hours=8, minutes=30)
    url = f"https://himawari8.nict.go.jp/img/D531106/1d/550/{utc_time.strftime('%Y/%m/%d/%H%M')[0:14]}000_0_0.png"
    return get_group_picture(url)


def get_yiyan():
    yiyan_type = {
        "a": "动画",
        "b": "漫画",
        "c": "游戏",
        "d": "文学",
        "e": "原创",
        "f": "来自网络",
        "g": "其他",
        "h": "影视",
        "i": "诗词",
        "j": "网易云",
        "k": "哲学",
        "l": "抖机灵",
        "其他":"动画"
    }
    url="https://v1.hitokoto.cn/"
    response = requests.get(url=url, proxies=NO_PROXY).json()
    if response.get("id"):
        message = response.get("hitokoto")+"   \n----"+(response["from"] if response["from"] else response["from_who"])+ " 分类: "+yiyan_type[response["type"]]
        return message
    else:
        return "疑似一言接口出错🧐"



if __name__ == '__main__':
    print(get_tel_message(".tel 114514", 0))
