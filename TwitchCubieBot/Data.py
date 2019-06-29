
from enum import Enum
import time

class Message:
    # Message class to store information about a message.
    def __init__(self, sender, message):
        self.sender = sender
        self.message = message
        self.timestamp = round(time.time())
    
    def get_message(self):
        return self.message

    def outdated(self):
        # Return if this message was sent less than 3 minutes ago
        return self.timestamp + 3 * 60 < time.time()
    
    def __repr__(self):
        return self.message

class MessageTypes(Enum):
    TEXT = 0
    NUMBERS = 1
    EMOTES = 2

class Collection:
    def __init__(self):
        self.text = {}
        self.numbers = {}
        self.emotes = {}

        self._accessor = [self.text, self.numbers, self.emotes]

    def set(self, sender, message, message_type):
        self._accessor[message_type.value][sender] = Message(sender, message)

    def clean(self):
        # Removes values older than 3 minutes

        for _dict in self._accessor:
            # List of keys to remove, as we can't remove from a dict during iteration
            to_remove = []

            for key in _dict:
                if _dict[key].outdated():
                    # Remove the item from the dict
                    to_remove.append(key)

            # Remove items from dict
            for key in to_remove:
                _dict.pop(key)

    def average(self, _min, _max):
        values = [self.numbers[key] for key in self.numbers if self.numbers[key] >= _min and self.numbers[key] <= _max]
        average = sum(values) / len(values)
        return average
    
    def vote(self, message_type):
        # Make a dict for voting
        vote_dict = {}
        for key in self._accessor[message_type.value]:
            value = self._accessor[message_type.value][key].get_message()
            if value in vote_dict:
                vote_dict[value] += 1
            else:
                vote_dict[value] = 1

        # Get max and sum from the values
        _max = max(vote_dict.values())
        _sum = sum(vote_dict.values())
        # Return the winning votes like: [(3, 0.4), (4, 0.4)] if the values 3 and 4 tied with 40% each.
        return [(key, _max / _sum) for key in vote_dict if vote_dict[key] == _max]

    def length(self, message_type):
        return len(self._accessor[message_type.value])
    
    def clear(self, message_type):
        return self._accessor[message_type.value].clear()