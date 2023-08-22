import random
import re

import requests
from urllib import parse


from global_config \
    import BASE_URL, BAN_FLAG, BAN_MESSAGE, ENABLE_FUNC, SELF_ID, NO_PROXY

def send_message(message, user_id, group_id=None, ban_flag=BAN_FLAG):
    """
    发送基本信息
    :param message: 消息内容
    :param user_id: 用户id
    :param group_id: 群组id
    :param ban_flag: 看看ban
    :return: None
    """

    encode_message = parse.quote(message)
    if group_id is not None:
        payload = f"{BASE_URL}send_msg?group_id={group_id}&message={encode_message}"
    else:
        payload = f"{BASE_URL}send_msg?user_id={user_id}&message={encode_message}"
    response = requests.get(url=payload, proxies=NO_PROXY)
    response.raise_for_status()
    return None

def ban_group(user_id, group_id=None, duration=600):
    if group_id is not None:
        payload = f"{BASE_URL}set_group_ban?group_id={group_id}&user_id={user_id}&duration={duration}"
    else:
        return None
    requests.get(url=payload, proxies=NO_PROXY)
    return None

def ban_whole_group(group_id=None, enable=True):
    if group_id is not None:
        payload = f"{BASE_URL}set_group_whole_ban?group_id={group_id}&enable={'true' if enable else 'false'}"
    else:
        return None
    requests.get(url=payload, proxies=NO_PROXY)
    return None

def get_message(message_id):
    """
    根据message id 获得信息
    :param message_id:
    :return:requests' json
    """
    payload = f"{BASE_URL}get_msg?message_id={message_id}"
    try:
        response = requests.get(url=payload, proxies=NO_PROXY)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("get message error.", e)
        return None
    return response.json()


def recall_message(message_id):
    """

    :param message_id:
    :return: Boolean 是否防撤回成功？
    """
    message = get_message(message_id).get('data')
    group_id = message.get('group_id')
    user_id = message.get('sender').get('user_id')
    nickname = message.get('sender').get('nickname')
    if group_id in ENABLE_FUNC.get('withdraw'):
        new_message = "🤗{0}撤回了:\n".format(nickname) + message.get('message')
        send_message(new_message, user_id, group_id)
        return True

    return False

def ban_message(user_id, group_id):
    """
    
    :param message_id: 
    :return: 
    """
    if BAN_MESSAGE:
        if group_id in ENABLE_FUNC.get('ban') and user_id != SELF_ID:
            new_message = "好似"
            send_message(new_message, user_id, group_id)

def get_random_str(random_length=10):
    """
    生成随机字符串
    :param random_length: int 字符串长提
    :return: str， 随机字符串
    """
    base_str="ABCDEFGHIJKLMNOBQRSTUVWXYZabcdefghijklmnopqrstuvwkyz0123456789"
    random_str=''.join([base_str[random.randrange(0,len(base_str))] for i in range(random_length)])
    return  random_str

def get_status_message(enable_func: dict, group_id=None):
    if group_id is None:
        return None
    message=f"{group_id} 现有权限如下："
    for key, val_list in enable_func.items():
        if group_id in val_list:
            message +=f"\n{key}   ⭕enable"
        else:
            message +=f"\n{key}   ❌disable"
    return message

def get_regex_group1(pattern:str, string:str):
    result = re.match(pattern=pattern, string=string)
    if result is None:
        return None
    else:
        return result.group(1)