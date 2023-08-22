from flask import Flask, request
from global_config import HTTP_PROXY, HTTPS_PROXY
import os
import time

import controller
import my_utils.timing as timing

os.environ["HTTP_PROXY"] = HTTP_PROXY
os.environ["HTTPS_PROXY"] = HTTPS_PROXY

app = Flask(__name__)


@app.route('/', methods=["POST"])
def listen_main_port():
    """
    监听端口以采取动作
    """
    response_dict = request.get_json()
    # print(response_dict)
    post_type = response_dict.get('post_type')

    if post_type == "message":
        controller.message_parse(response_dict)
    elif post_type == "notice":
        controller.notice_parse(response_dict)

    return ''


if __name__ == "__main__":
    timing.run_clock()
    app.run(host="127.0.0.1", port=5701)
