import random
import re
import time

from global_config import (
    ANTI_RECALL_FLAG,
    ANTI_RECALL_LIST,
    ENABLE_FUNC,
    WEATHER_POSITION,
    SELF_ID,
    BOT_NAME,
    TIME_CONFIG,
    AUTH_GROUP,
    ROOT_ID
)
from base_api import (
    recall_message,
    send_message,
    ban_message,
    get_status_message,
    get_regex_group1
)
from my_utils.small_func import (
    get_gaokao_message,
    get_jrrp_message,
    get_anke_message,
    get_ip_message,
    get_tel_message,
    get_earth,
    get_yiyan,
    get_moyu_image
)
import my_utils.weather as weather
import my_utils.setu as setu
from my_utils.chatgpt import botGPT
from my_utils.cq_code import get_reply, get_at, get_poke
from my_utils.bot_log import Logger

BOT_START_TIME = time.time()

botLog = Logger()

AlphaBeta = ",\.\?!\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\u4e00-\u9fa5"

BOT_START_TIME = time.time()

INST_LIST = [
    '.help       查询指令(可选参数查询具体指令)',
    '.chat       ChatGPT',
    '.setu       随机色图',
    '.wea        🌞今日天气',
    '----------------',
    '指令、参数、正文内容分别用空格隔开, 指令前中英文句号皆可',
]

SMALL_INST_LIST = [
    '.echo       echo hello world!🖥️，你的第一款shell何必是*sh\n'
    '.rd         安科🤖，rd后紧跟数字(数字前不能空格) 正文便可以在[0, num]间进行正文的安科\n',
    '.gaokao     高考倒计时⏰，大学要逃走了😭\n',
    '.jrrp       今日运势🧧，看看你的运气🙏\n',
    '.ip         查询IP🤓，我超盒😰\n',
    '.tel        查询电话信息😱，esu啊😰\n',
    '.earth      日本向日葵8号卫星遥感图🌏，每十分钟更新，由于网站设置，仅能观看半小时前的遥感图\n',
    '.yiyan      一言接口，返回一句话格言📕'
]

CHAT_INST_LIST = [
    '.chat       采用预设进行chatgpt🤖对话',
    '.get        你们都聊了什么🧐',
    '.preset     定制你的老婆🙌',
    '.clear      你是？不能忘记的人😭',
    '.init       回归出厂设置😇',
    '---------------',
    '遇到出错信息就clear一下，chatgpt就是这么难用😡'
]

WEA_INST_LIST = [
    '.wea       查看6小时天气预报🥶',
    '.weaset    设置你群默认城市👁️',
    '.weaday    将来5天天气数据🥵',
    '---------------',
    '支持可选城市,拼音对或英文名皆可.'
]


def message_parse(data_dict):
    """
    处理指令、非指令信息
    :param data_dict: cqhttp格式信息
    :return: None
    """
    message_id = data_dict.get('message_id')
    message_type = data_dict.get('message_type')
    message = data_dict.get('raw_message')
    user_id = data_dict.get('user_id')
    group_id = data_dict.get('group_id')
    sender = data_dict.get('sender')
    role = sender.get('role')
    nickname = sender.get('nickname')

    try:
        if message[0] == '.' or message[0] == '。':
            instruct_control(message, message_type, user_id, group_id, message_id, role, nickname)
        else:
            pass
    except Exception as e:
        botLog.info(str(e))

def instruct_control(message:str, message_type, user_id, group_id, message_id, role, nickname):
    """

    :param message:
    :param user_id:
    :param group_id:
    :param message_id:
    :return:
    """
    try:
        errMessage = "😲指令输入出错😲"
        resMessage = "🧐你似乎进入了没有权限的荒原"
        priMessage = "😥指令只对群聊有效捏"
        banMessage = "🤗该指令未被授权捏"

        pattern = r'^\.(\w+)\s*'
        funcPattern = r'^\.\w+\s*(\w+)\s*'
        # print(message, type(message))
        if message[0] == "。":
            message = "." + message[1:]
        instruction = get_regex_group1(pattern=pattern, string=message)
        if instruction is None:
            return
        # help 打印指令
        if group_id not in AUTH_GROUP:
            if user_id == ROOT_ID and instruction == "active":
                AUTH_GROUP.append(group_id)
                send_message("已激活bot",user_id, group_id)
            return
        if user_id == ROOT_ID and instruction == "deactive":
            while group_id in AUTH_GROUP:
                AUTH_GROUP.remove(group_id)
            send_message("你的名字是...什么?",user_id, group_id)
            return

        if instruction == "help":
            help_control(message, user_id, group_id)
            return

        elif instruction == "status":
            newMessage = status_all(group_id)
            send_message(newMessage, user_id, group_id)
            return

        # grant 群聊授权指令
        elif instruction == "grant":
            if group_id is None:
                send_message(priMessage, user_id, group_id)
                return
            func = re.match(pattern=funcPattern, string=message).group(1)
            funcEnableList = ENABLE_FUNC.get(func)
            if funcEnableList is None:
                send_message(errMessage, user_id, group_id)
            elif role == "member" and user_id != ROOT_ID:
                send_message(resMessage, user_id, group_id)
            elif group_id not in funcEnableList:
                funcEnableList.append(group_id)
                send_message("🥳授权 {0} 成功".format(func), user_id, group_id)
            else:
                send_message("🧐 {0} 已授权".format(func), user_id, group_id)
            return

        # revoke 群聊revoke指令
        elif instruction == "revoke":
            if group_id is None:
                return send_message(priMessage, user_id, group_id)
            func = re.match(pattern=funcPattern, string=message).group(1)
            funcEnableList = ENABLE_FUNC.get(func)
            if funcEnableList is None:
                send_message(errMessage, user_id, group_id)
            elif role == "member":
                send_message(resMessage, user_id, group_id)
            elif group_id in funcEnableList:
                funcEnableList.remove(group_id)
                send_message("🥳权限 {0} 收回".format(func), user_id, group_id)
            else:
                send_message("🧐 {0} 已禁用".format(func), user_id, group_id)

        # 不需要授权的基础功能
        # 简单测试hello world
        elif instruction == "echo":
            newMessage = message.replace('.echo', '').lstrip()
            send_message(newMessage, user_id, group_id)

        # 高考倒计时
        elif instruction == "gaokao":
            newMessage = get_gaokao_message()
            send_message(newMessage, user_id, group_id)

        # 今日运势
        elif instruction == "jrrp":
            newMessage = get_jrrp_message(message_id, user_id, nickname)
            send_message(newMessage, user_id, group_id)

        elif instruction == "ip":
            newMessage = get_ip_message(message, message_id)
            send_message(newMessage, user_id, group_id)
        elif instruction == "tel":
            newMessage = get_tel_message(message, message_id)
            send_message(newMessage, user_id, group_id)

        elif len(instruction) >= 2 and instruction[0:2] == "rd":
            anke_control(instruction, message, user_id, group_id, message_id)
        elif instruction == "earth":
            newMessage = get_earth()
            send_message(newMessage, user_id, group_id)
        elif instruction == "yiyan":
            newMessage = get_yiyan()
            send_message(newMessage, user_id, group_id)
        elif instruction == "moyu":
            newMessage = get_moyu_image()
            send_message(newMessage, user_id, group_id)

        # 需要授权的功能
        # chatgpt

        elif instruction in ['clear', 'chat', 'preset', 'init', 'get']:
            if group_id not in ENABLE_FUNC.get("chat"):
                send_message(banMessage, user_id, group_id)
                return
            gpt_control(instruction, message, user_id, group_id, message_id)
        elif instruction == "setu":
            if group_id not in ENABLE_FUNC.get("setu"):
                send_message("不可以色色！", user_id, group_id)
                return
            setu_control(message, user_id, group_id)
        # elif instruction == "genshin":
        #     if group_id not in ENABLE_FUNC["genshin"]:
        #         send_message("原神怎么你了？", user_id, group_id)
        #         return
        elif instruction in ["wea", "weaset", "weaday"]:
            if group_id not in ENABLE_FUNC.get("wea"):
                send_message(banMessage, user_id, group_id)
                return
            weather_control(instruction, message, user_id, group_id)



    except Exception as e:
        botLog.info("处理指令出错:{0}".format(str(e)))
        send_message("处理指令出错:{0}".format(str(e)), user_id, group_id)


def help_control(message, user_id, group_id):
    realMessage = message.replace(".help", '').lstrip().rstrip()
    if realMessage in ["rd","gaokao","jrrp","earth","ip","tel","echo","yiyan"]:
        newMessage = "".join(SMALL_INST_LIST)
    elif realMessage in ['clear', 'chat', 'preset', 'init', 'get']:
        newMessage = "\n".join(CHAT_INST_LIST)
    elif realMessage in ["wea", "weaset", "weaday", "weather"]:
        newMessage = "\n".join(WEA_INST_LIST)
    elif realMessage == "setu":
        newMessage = "setu支持空格隔开的tag，请注意不要请求太多让其他人服务器💣了"
    else:
        newMessage = "\n".join(INST_LIST)
    send_message(newMessage, user_id, group_id)


def anke_control(instruction, message, user_id, group_id, message_id):
    if len(instruction) > 2:
        try:
            range_num = int(instruction[2:])
        except Exception as e:
            botLog.info("安科数值范围转换错误")
            return
        result = re.match(pattern=rf"^\.rd\w+\s+([\w{AlphaBeta}]+)", string=message)

        if result is None:
            real_message = "你没有指定什么事情"
        else:
            real_message = result.group(1)
        newMessage = get_anke_message(real_message, message_id, range_num)
    else:
        result = re.match(pattern=fr"^\.rd\s+([\w{AlphaBeta}]+)", string=message)
        if result is None:
            real_message = "你没有指定什么事情"
        else:
            real_message = result.group(1)
        newMessage = get_anke_message(real_message, message_id)
    send_message(newMessage, user_id, group_id)


def gpt_control(instruction, message, user_id, group_id, message_id):
    """

    :param instruction:
    :param message:
    :param user_id:
    :param group_id:
    :param message_id:
    :return:
    """
    replyDict = {
        'clear': '已重置对话',
        'preset': '预设成功',
        'get': '看看我的状态！',
        'chat': '🤯gpt baozhale锟斤拷',
        'init': '🤖格式化完毕',
    }
    replyMessage = replyDict[instruction]
    nowMessage = message.replace("." + instruction, "").lstrip()
    try:
        if instruction == 'chat':
            if message_id is None:
                replyMessage = botGPT.chat(nowMessage, user_id, group_id)
            else:
                replyMessage = get_reply(message_id) + get_at(user_id) \
                               + " " + botGPT.chat(nowMessage, user_id, group_id)
        elif instruction == 'clear':
            botGPT.clear(user_id, group_id)
        elif instruction == 'get':
            replyMessage = botGPT.get(user_id, group_id)
        elif instruction == "preset":
            botGPT.preset(nowMessage, user_id, group_id)
        elif instruction == "init":
            botGPT.init(user_id, group_id)
        send_message(replyMessage, user_id, group_id)
    except Exception as e:
        botLog.info("gpt出错:{0}".format(str(e)))
        send_message(str(e), user_id, group_id)


def weather_control(instruction, message, user_id, group_id):
    if instruction == "weaset":
        newMessage = message.replace(".weaset", '').lstrip()
        if newMessage == "":
            return None
        else:
            WEATHER_POSITION[group_id] = newMessage
            send_message(f"🌝已设置你群城市：{newMessage}", user_id, group_id)
            return None
    elif instruction == "wea":
        newMessage = message.replace(".wea", '').lstrip().rstrip()
        if newMessage == "":
            if WEATHER_POSITION.get(group_id):
                position = WEATHER_POSITION[group_id]
            else:
                send_message("🤯默认城市是什么🤯", user_id, group_id)
                return 
        else:
            position = newMessage
        message = weather.get_weather_hour(position)
        send_message(message, SELF_ID, group_id)
    elif instruction == "weaday":
        newMessage = message.replace(".weaday", '').lstrip().rstrip()
        if newMessage == "":
            if WEATHER_POSITION.get(group_id):
                position = WEATHER_POSITION[group_id]
            else:
                send_message("🤯默认城市是什么🤯", user_id, group_id)
                return
        else:
            position = newMessage
        message = weather.get_weather_daily(position)
        send_message(message, SELF_ID, group_id)

    warning_message = weather.get_weather_warning(position)
    if warning_message is not None:
        send_message(warning_message, SELF_ID, group_id)


def setu_control(message: str, user_id, group_id):
    nowMessage = message.replace(".setu", "").lstrip().rstrip()
    if nowMessage == "":
        newMessage = setu.get_setu()
    else:
        newList = re.split(r'[;!！？?.,，。\s]\s*', nowMessage)
        newMessage = setu.get_tag_setu(newList)

    send_message(newMessage, user_id, group_id)


def status_all(group_id):
    now_time = int(time.time() - BOT_START_TIME)
    days, seconds = divmod(now_time, 60 * 60 * 24)
    hours, seconds = divmod(seconds, 60 * 60)
    minutes, seconds = divmod(seconds, 60)
    newMessage = f"===={BOT_NAME}====\n" \
                 f"存活时长:{days}天 {hours}时 {minutes}分 {seconds}秒\n" \
                 f"------------------------\n" \
                 f"{get_status_message(ENABLE_FUNC, group_id)}\n" \
                 f"本群天气默认城市: {WEATHER_POSITION[group_id] if WEATHER_POSITION.get(group_id) else '请设置默认城市'}\n" \
                 f"本群定时播报时间: {TIME_CONFIG['hour']}时{TIME_CONFIG['minute']}分\n"
    return newMessage


def notice_parse(data_dict):
    notice_type = data_dict.get('notice_type')
    user_id = data_dict.get('user_id', None)
    group_id = data_dict.get('group_id', None)
    message_id = data_dict.get('message_id', None)
    sub_type = data_dict.get('sub_type', None)

    if notice_type == "group_recall" and ANTI_RECALL_FLAG:
        if recall_message(message_id):
            return None

        judge_recall = random.random()
        if judge_recall <= 0.4:
            send_message(ANTI_RECALL_LIST[random.randint(0, len(ANTI_RECALL_LIST) - 1)], user_id, group_id)
    elif notice_type == "group_ban" and sub_type == "ban":
        ban_message(user_id, group_id)


if __name__ == "__main__":
    print(help_control(".help wea", 1, 1))
