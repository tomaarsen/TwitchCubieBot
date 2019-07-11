
import logging, json, os, sys
logger = logging.getLogger(__name__)

class Settings:
    """ Loads data from settings.txt into the bot """
    def __init__(self, path):
        self.path = path
    
    def get_settings(self):
        logger.debug("Loading settings.txt file...")
        try:
            # Try to load the file using json.
            # And pass the data to the Bot class instance if this succeeds.
            with open(self.path, "r") as f:
                settings = f.read()
                settings_dict = json.loads(settings)
                logger.debug("Settings loaded into Bot.")
                return [settings_dict[key] for key in settings_dict]

        except ValueError:
            logger.error("Error in settings file.")
            raise ValueError("Error in settings file.")
            
        except FileNotFoundError:
            # If the file is missing, create a standardised settings.txt file
            # With all parameters required.
            logger.error("Please fix your settings.txt file that was just generated.")
            with open(self.path, 'w') as f:
                standard_dict = {
                                    "Host": "irc.chat.twitch.tv",
                                    "Port": 6667,
                                    "Channel": "#<channel>",
                                    "Nickname": "<name>",
                                    "Authentication": "oauth:<auth>",
                                    "DeniedUsers": ["streamelements", "marbiebot", "moobot"],
                                    "AllowedRanks": ["broadcaster", "moderator"],
                                    "AllowedPeople": [],
                                    "LookbackTime": 30
                                }
                f.write(json.dumps(standard_dict, indent=4, separators=(',', ': ')))
                raise ValueError("Please fix your settings.txt file that was just generated.")
