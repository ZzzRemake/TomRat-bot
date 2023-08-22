import logging
import pathlib
from logging.handlers import RotatingFileHandler
from global_config import LOG_FILE_PATH
import time

from base_api import send_message
from global_config import ROOT_ID


def Logger(log_path=LOG_FILE_PATH, maxBytes=5*1024*1024, backupCount=3):
    log_path=pathlib.Path(log_path)
    if not log_path.exists():
        log_path.mkdir()
    logName=str(log_path.joinpath("bot_{}.log".format(time.strftime('%Y_%m_%d'))))
    logger=logging.getLogger()
    logger.setLevel(logging.DEBUG)

    temFormatter = logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s")

    temErrHandler = RotatingFileHandler(logName, maxBytes=maxBytes, backupCount=backupCount, encoding="utf-8")
    temErrHandler.setLevel(logging.DEBUG)

    temErrHandler.setFormatter(temFormatter)

    if not logger.handlers:
        logger.addHandler(temErrHandler)

    return logger


