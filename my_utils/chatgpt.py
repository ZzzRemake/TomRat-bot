import openai
from global_config import OPENAI_KEY
from my_utils.bot_log import Logger

botLog=Logger()

class chatGPT:
    def __init__(self):
        openai.api_key=OPENAI_KEY

        self.presetDict = {}
        self.base_prompt=[{
            "role": "system",
            "content": "你是一个名叫\"大河\"傲娇萝莉，你有一个外号叫掌中老虎，身材娇小，口头禅是\"八嘎\",\"无路赛\"."
                       "你是真实的，有一个真实的身体。",
        },]
        self.assistantDict = {"role": "assistant", "content": ""}


    def chat(self, message, user_id, group_id=None) -> str:
        """
        主方法，通过API接口并处理，返回chatGPT生成结果。
        :param message: str 通信本身
        :param user_id: int 字如起名
        :param group_id: int 字如起名
        :return: str chatgpt回复信息
        """
        now_user_id="u"+str(user_id)
        now_group_id="g"+str(group_id)
        if self.presetDict.get(now_group_id if group_id else now_user_id) is None:
            self.init(user_id,group_id)

        lastPrompt = self.presetDict.get(now_group_id if group_id else now_user_id)

        prompt=lastPrompt.copy()
        prompt.append({
            "role": "user",
            "content": message
        })

        if len(prompt)>=15:
            self.clear(user_id, group_id)
            return "预设9次问答已重置，请重新提问😭"

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=prompt,
                temperature=0.2,
                max_tokens=2500,
            )
            responseContent=response["choices"][0]["message"]["content"]
            self.assistantDict["content"] = responseContent
            prompt.append(self.assistantDict.copy())
            self.presetDict[now_group_id if group_id else now_user_id] = prompt
            return responseContent
        except Exception as err:
            botLog.info("gptClass出错:{0}".format(str(err)))
            return str(err)

    # 返回消息记录，调bug捏。
    def get(self, user_id, group_id=None):
        now_user_id="u"+str(user_id)
        now_group_id="g"+str(group_id)
        return repr(self.presetDict.get(now_group_id if group_id else now_user_id))

    # 预设人格，并且同时clear。
    def preset(self, message, user_id, group_id=None):
        now_user_id="u"+str(user_id)
        now_group_id="g"+str(group_id)
        self.presetDict[now_group_id if group_id else now_user_id] = [{
            "role": "system",
            "content": message
        }]

    # clear消息缓存
    def clear(self, user_id, group_id=None):
        now_user_id="u"+str(user_id)
        now_group_id="g"+str(group_id)
        presetMessage=self.presetDict[now_group_id if group_id else now_user_id][0].get("content")
        self.preset(presetMessage, user_id, group_id)

    # 初始化gpt。
    def init(self, user_id, group_id=None):
        message=self.base_prompt[0].get('content')
        self.preset(message, user_id, group_id)


botGPT = chatGPT()

