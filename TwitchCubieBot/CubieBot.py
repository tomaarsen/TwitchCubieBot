from TwitchWebsocket import TwitchWebsocket
import json, time, logging, os, string

if __name__ == "__main__":
    from Log import Log
    Log(__file__)

from TwitchCubieBot.Settings import Settings
from TwitchCubieBot.Data import Collection
from TwitchCubieBot.Data import MessageTypes
from TwitchCubieBot.View import MessageSource
from TwitchCubieBot.View import View

class CubieBot:
    def __init__(self):
        self.host = None
        self.port = None
        self.chan = None
        self.nick = None
        self.auth = None
        self.capability = "tags"
        self.denied_users = None
        self.allowed_ranks = None
        self.allowed_people = None
        self.lookback_time = None
        self.prev_command_time = 0
        self.collection = Collection()
        self.view = View(self)
    
    def update_settings(self):
        # Fill previously initialised variables with data from the settings.txt file
        Settings(self)

    def start(self):
        self.ws = TwitchWebsocket(host=self.host, 
                                  port=self.port,
                                  chan=self.chan,
                                  nick=self.nick,
                                  auth=self.auth,
                                  callback=self.message_handler,
                                  capability=self.capability,
                                  live=True)
        self.ws.start_nonblocking()

    def stop(self):
        try:
            self.ws.join()
        except AttributeError:
            # If self.ws has not yet been instantiated. 
            # In this case we have essentially already stopped
            pass

    def set_settings(self, host, port, chan, nick, auth, denied_users, allowed_ranks, allowed_people, lookback_time):
        self.host = host
        self.port = port
        self.chan = chan
        self.nick = nick
        self.auth = auth
        self.denied_users = denied_users
        self.allowed_ranks = allowed_ranks
        self.allowed_people = allowed_people
        self.lookback_time = lookback_time

    def message_handler(self, m):
        try:
            if m.type == "366":
                logging.info(f"Successfully joined channel: #{m.channel}")
            
            elif m.type == "NOTICE":
                logging.info(m.message)
                
            elif m.type == "PRIVMSG":
                # Look for commands.
                if m.message.startswith("!average") and self.check_permissions(m) and self.check_timeout():
                    self.command_average(m)
                elif m.message.startswith("!vote") and self.check_permissions(m) and self.check_timeout():
                    self.command_vote(m)
                else:
                    # Parse message for potential numbers/votes and emotes.
                    self.check_for_numbers(m.message, m.user)
                    self.check_for_text(m.message, m.user)
                    self.check_for_emotes(m)

        except Exception as e:
            logging.error(e)

    def check_timeout(self):
        # Returns true if previous command was more than 5 seconds ago.
        # Prevents multiple people from attempting to call the same vote/average, 
        # and getting incorrect results the 2nd time
        return self.prev_command_time + 5 < time.time()

    def check_permissions(self, m):
        for rank in self.allowed_ranks:
            if rank in m.tags["badges"]:
                return True
        for name in self.allowed_people:
            if m.user.lower() == name.lower():
                return True
        return False

    def check_denied_users(self, sender):
        # Check if sender is not a denied user (generally another bot).
        return sender in self.denied_users

    def command_average(self, m):
        # Clean up the collection by removing old values.
        self.collection.clean(self.lookback_time)

        # Get the min and max from the message
        _min, _max = self.check_valid_min_max(m.message)

        # If there are errors, _min and _max will be False.
        if _min != False:
            if self.collection.length(MessageTypes.NUMBERS) > 0:
                # Calculate Average.
                average = self.collection.average(_min, _max)
                
                # Send outputs.
                out = "/me Average is {:.2f}{}.".format(average, "%" if _max == 100 else "")
                source = MessageSource.AVERAGE_RESULTS
                
                # Clear out the saved data
                self.collection.clear(MessageTypes.NUMBERS)

                # Reset previous command time
                self.prev_command_time = time.time()
            else:
                out = "No recent numbers found to take the average from."
                source = MessageSource.AVERAGE_COMMAND_ERRORS
            logging.info(out)
            self.view.output(out, source)

    def command_vote(self, m):
        # Clean up the collection by removing old values.
        self.collection.clean(self.lookback_time)
        
        # Find out whether sender wants to vote using numbers, letters or emotes.
        message_type = self.check_vote_type(m.message)
        
        # If there are votes
        if self.collection.length(message_type) > 0:
            # Get the votes
            votes = self.collection.vote(message_type)
            # Turn votes into a message
            if len(votes) == 1:
                out = "/me {} won with {:.2f}%.".format(votes[0][0], votes[0][1] * 100)
            else:
                seperator = ", "
                # If the vote is with emotes, we don't want commas directly after the emotes, or they will not turn into actual emotes in the chat.
                if message_type == MessageTypes.EMOTES:
                    seperator = " , "
                out = "/me " + seperator.join([str(vote[0]) for vote in votes[:-1]]) + " and " + str(votes[-1][0]) + f" tied with {votes[0][1] * 100:.2f}% each."
            source = MessageSource.VOTING_RESULTS
            self.collection.clear(message_type)

            # Reset previous command time
            self.prev_command_time = time.time()
        else:
            out = "No votes found."
            source = MessageSource.VOTING_COMMAND_ERRORS
        logging.info(out)
        self.view.output(out, source)

    def parse_number(self, message, sender):
        # Stripping message potentially containing a number of illegal characters.
        if self.check_denied_users(sender):
            return None
        
        # Remove percentages, and replace commas with dots
        remove = {"%":"", ",":"."}
        for i in remove:
            message = message.replace(i, remove[i])

        # Split "8/10" by /, and disregard everything after the first /.
        index = message.find("/")
        if index != -1:
            message = message[:index]

        # Split by spaces, force message to be a list
        message = message.split()
        
        # Check for each word if it's a number
        for m in message:
            try:
                return float(m)
            except ValueError:
                pass
        
        return None

    def check_vote_type(self, message):

        message_list = message.split()
        # If '!vote emotes', '!vote emote', '!vote emoji' or '!vote emojis'.
        if len(message_list) == 2 and message_list[1].startswith(("emote", "emoji")):
            return MessageTypes.EMOTES
        
        # If there is a min and a max
        if len(message_list) == 2 and message_list[1].startswith(("number", "value", "digit")):
            return MessageTypes.NUMBERS
        
        # Otherwise:
        return MessageTypes.TEXT

    def check_valid_min_max(self, message):

        # Extract parameters from a command.
        try:
            # Attempt to get a min and a max value from the command
            _min = float(message.split()[1])
            _max = float(message.split()[2])

            if _min >= _max:
                out = "Parameter Error, max should be larger or equal to min."
            else:
                # If values are proper, return them
                return _min, _max

        except:
            out = "Parameter Error, min and max values are not numbers."
        logging.info(out)
        source = MessageSource.AVERAGE_COMMAND_ERRORS
        self.view.output(out, source)
        # Return False in all other cases
        return False, False

    def check_for_numbers(self, message, sender):
        # Check if the message contains a number.
        for m in message.split():
            value = self.parse_number(m, sender)
            # Type of msg is only a float if a number was found.
            if type(value) == float:
                self.view.output(value, MessageSource.NUMBERS)
                self.collection.set(sender, value, MessageTypes.NUMBERS)
                return value
        return False

    def check_for_text(self, message, sender):
        # Check if the message contains a vote.
        if self.check_denied_users(sender):
            return False

        message_list = message.upper().split()
        first_word = message_list[0] # Also guaranteed to be upper
        first_letter = first_word[0] # Also guaranteed to be upper

        # If the first letter is a letter in the alphabet
        # and the entire range until the first space contains only that letter
        if first_letter in string.ascii_uppercase and first_word == first_letter * len(first_word):
            
            # Remove "I will/can/do" messages:
            # If sentence starts with "I"
            # and the sentence contains more than 1 word
            # and the second word contains at least 2 letters.
            if first_letter == "I" and len(first_word) == 1 and len(message_list) > 1 and len(message_list[1]) > 2:
                return False

            # Remove "D I A L":
            # If all words are 1 letter long
            # and the sentence with all spaces removed is NOT equal to first letter placed len(message_list) in a row
            if len([i for i in message_list if len(i) == 1]) == len(message_list) and "".join(message_list) != len(message_list) * first_letter:
                return False
            
            self.view.output(first_letter, MessageSource.VOTES)
            self.collection.set(sender, first_letter, MessageTypes.TEXT)
            return True
        
        return False
    
    def check_for_emotes(self, m):
        emotes = m.tags["emotes"]
        # If there are no emotes, return
        if len(emotes) == 0:
            return

        # In the form of "678075:0-7/58765:9-19,107-117"
        emote_list = emotes.split("/")
        # In the form of ["678075:0-7", "58765:9-19,107-117"]
        for emote in emote_list:
            index_string = emote.split(":")[1]
            # In the form of "9-19,107-117"
            index_string_list = index_string.split(",")
            # In the form of ["9-19", "107-117"]
            for index in index_string_list:
                start = int(index.split("-")[0])
                end = int(index.split("-")[1]) + 1 # Add 1 for easy slicing
                self.collection.set(m.user, m.message[start:end], MessageTypes.EMOTES)

if __name__ == "__main__":
    bot = CubieBot()
    bot.update_settings()
    bot.start()
    # This method of endlessly sleeping, while the bot itself does not hold up the thread allows
    # other bots, such as my TwitchCubieBotGUI to start the bot more conveniently.
    try:
        while True:
            time.sleep(1000)
    except (KeyboardInterrupt, SystemExit):
        bot.stop()

