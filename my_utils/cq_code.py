from base_api import get_random_str

def get_at(qq, name="") -> str:
    codeDict={
        "type": "at",
        "data": {
            "qq": qq,
            "name": name,
        }
    }
    return get_cq_code(codeDict)

def get_reply(message_id:str, text:str="", qq:str="") -> str:
    codeDict={
        "type": "reply",
        "data": {
            "id": message_id
        }
    }
    return get_cq_code(codeDict)

def get_poke(qq):
    codeDict={
        "type": "poke",
        "data":{
            "qq",qq
        }
    }
    return get_cq_code(codeDict)

def get_group_picture(url):
    codeDict = {
        "type": "image",
        "data":{
            "file": get_random_str() + ".image",
            "subType": 0,
            "url": str(url),
            "cache": 0
        },

    }
    return get_cq_code(codeDict)

def get_cq_code(codeDict: dict) -> str:
    dataStr=""
    for key, value in codeDict["data"].items():
        dataStr+=",{0}={1}".format(key,value)
    cqCode="[CQ:{0}{1}]".format(codeDict["type"], dataStr)
    return cqCode