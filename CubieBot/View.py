
from enum import Enum, auto
import logging, json
logger = logging.getLogger(__name__)

class MessageSource(Enum):
    AVERAGE_RESULTS = auto()
    AVERAGE_COMMAND_ERRORS = auto()
    VOTING_RESULTS = auto()
    VOTING_COMMAND_ERRORS = auto()
    VOTES = auto()
    NUMBERS = auto()

# View class which can easily be overridden to change what should be output, and where
class View:
    def __init__(self, bot):
        self.bot = bot
        self.send_to_chat = [MessageSource.AVERAGE_RESULTS, MessageSource.AVERAGE_COMMAND_ERRORS, MessageSource.VOTING_RESULTS, MessageSource.VOTING_COMMAND_ERRORS]
    
    def output(self, message, source):
        if source in self.send_to_chat:
            self.bot.ws.send_message(message)
