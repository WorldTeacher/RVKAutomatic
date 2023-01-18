import logging
import os

class log:
    def __init__(self) -> None:
        logging.basicConfig(filename='data/logs/test.log',level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.bot_log = logging.getLogger('bot')
    def bot_info(self, message):
        self.bot_log.info(message)
    def bot_debug(self, message):
        self.bot_log.debug(message)
    def bot_error(self, message):
        self.bot_log.error(message)
    def bot_warning(self, message):
        self.bot_log.warning(message)
    def bot_critical(self, message):
        self.bot_log.critical(message)