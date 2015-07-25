import logging

from errbot import BotPlugin
from errbot import botcmd

from twilio.rest.lookups import TwilioLookupsClient

import phonenumbers


class TwilioLookup(BotPlugin):
    """An err plugin for retrieving information on phone numbers using Twilio
    Lookup."""
    min_err_version = '1.6.0'
    max_err_version = '2.3.0'

    def activate(self):
        super(TwilioLookup, self).activate()

        if self.config is not None:
            self.TWILIO_ACCOUNT_SID = self.config.get('TWILIO_ACCOUNT_SID',
                                                      None)
            self.TWILIO_AUTH_TOKEN = self.config.get('TWILIO_AUTH_TOKEN',
                                                     None)
            if self.TWILIO_ACCOUNT_SID and self.TWILIO_AUTH_TOKEN:
                self.lookup = TwilioLookupsClient(self.TWILIO_ACCOUNT_SID,
                                                  self.TWILIO_AUTH_TOKEN)
            else:
                logging.info("Not starting TwilioLookup, configuration "
                             "missing TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN")
        else:
            logging.info("Not starting TwilioLookup, plugin not configured.")

    @botcmd
    def lookup(self, message, args):
        return message
