import requests
import random
from base_api import get_random_str
from my_utils.bot_log import Logger
from global_config import NO_PROXY

botLog=Logger()
def get_tag_setu(tag:list):
    url = "https://image.anosu.top/pixiv/json"
    params = {
        "num":1,
        "r18":0,
        "keyword":"|".join(tag),
        "db":0
    }
    response = requests.get(url=url, params=params, proxies=NO_PROXY).json()
    if len(response)==0:
        botLog.info("setu with tag error.")
        return "似乎搜不到呢😭"
    else:
        message =""
        for data in response:
            message += f"[CQ:image,file={get_random_str()}.image,subType=0,url={data['url']}]\npid: {data['pid']}\n" \
                       f"tag: {','.join([data['tags'][i] for i in range(0, min(3, len(data['tags'])) )])}\n"
        return message

def get_setu():
    url = "https://moe.anosu.top/api/"
    params = {
        "type":"json",
        "sort":"pixiv",
    }
    response = requests.get(url=url, params=params, proxies=NO_PROXY).json()
    if response.get("code")==200:
        return f"[CQ:image,file={get_random_str()}.image,subType=0,url={response['pics'][0]}]"
    else:
        botLog.info("setu with no tag error.")
        return "pixiv图片接口似乎出错了？"


if __name__ == "__main__":
    print(get_tag_setu("furry"))
    print(get_setu())