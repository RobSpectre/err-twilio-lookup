import logging

from errbot import BotPlugin
from errbot import botcmd

from twilio.rest.lookups import TwilioLookupsClient
from twilio.rest.exceptions import TwilioRestException

import phonenumbers


class TwilioLookup(BotPlugin):
    """An err plugin for retrieving information on phone numbers using Twilio
    Lookup."""
    min_err_version = '1.6.0'
    max_err_version = '3.0.0'

    def activate(self):
        if self.config is not None:
            self.TWILIO_ACCOUNT_SID = self.config.get('TWILIO_ACCOUNT_SID',
                                                      None)
            self.TWILIO_AUTH_TOKEN = self.config.get('TWILIO_AUTH_TOKEN',
                                                     None)
            if self.TWILIO_ACCOUNT_SID and self.TWILIO_AUTH_TOKEN:
                super(TwilioLookup, self).activate()
                self.lookup = TwilioLookupsClient(self.TWILIO_ACCOUNT_SID,
                                                  self.TWILIO_AUTH_TOKEN)
            else:
                logging.info("Not starting TwilioLookup, configuration "
                             "missing TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN")
        else:
            logging.info("Not starting TwilioLookup, plugin not configured.")

    @botcmd
    def lookup(self, message, args):
        number = self.sanitize_number(args)

        if hasattr(number, "country_code"):
            formatter = phonenumbers.PhoneNumberFormat.E164
            number = phonenumbers.format_number(number, formatter)
            number = self.lookup_e164_number(number)

            if hasattr(number, "national_format"):
                yield "I found a {0} {1} number " \
                      "{2}.".format(number.country_code,
                                    number.carrier['type'],
                                    number.national_format)

                if number.carrier['name'] == "Twilio":
                    yield "My heart glows as it is a :twilio: Twilio " \
                          "number :twilio:."
                else:
                    yield "It tragically belongs to " \
                          "{0}".format(number.carrier['name'])

        yield number

    def lookup_e164_number(self, number_string):
        try:
            return self.lookup.phone_numbers.get(number_string,
                                                 include_carrier_info=True)
        except TwilioRestException as e:
            return "Could not find information on phone number " \
                   "{0}: {1}".format(number_string, e)

    def sanitize_number(self, number):
        if not any(character.isdigit() for character in number):
            return "Could not find a number here: " \
                   "{0}".format(number)
        if any(character.isalpha() for character in number):
            split = number.split(" ")
            if len(split) == 2:
                number = phonenumbers.parse(split[0], split[1])
            else:
                # Gross hack as PhoneNumberMatcher doesn't support indexing.
                for match in phonenumbers.PhoneNumberMatcher(number, "US"):
                    number = match.number
                    break
        else:
            number = phonenumbers.parse(number)

        number = self.validate_number(number)

        return number

    def validate_number(self, number):
        if not phonenumbers.is_possible_number(number):
            return "This number is not possible: " \
                   "{0}".format(number)
        if not phonenumbers.is_valid_number(number):
            return "This number is not valid: " \
                   "{0}".format(number)

        return number
