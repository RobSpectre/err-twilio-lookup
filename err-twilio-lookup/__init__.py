from errbot import BotPlugin
from errbot import botcmd

from twilio.rest.lookups import TwilioLookupsClient
from twilio.rest.exceptions import TwilioRestException

import phonenumbers


class TwilioLookup(BotPlugin):
    """An err plugin for retrieving information on phone numbers using Twilio
    Lookup."""
    min_err_version = '1.6.0'

    def get_configuration_template(self):
        return {'TWILIO_ACCOUNT_SID': "ACxxxxx",
                'TWILIO_AUTH_TOKEN': "yyyyyyyy"
                }

    def check_configuration(self, configuration):
        if configuration is not None:
            self.TWILIO_ACCOUNT_SID = configuration.get('TWILIO_ACCOUNT_SID',
                                                        None)
            self.TWILIO_AUTH_TOKEN = configuration.get('TWILIO_AUTH_TOKEN',
                                                       None)
            if self.TWILIO_ACCOUNT_SID and self.TWILIO_AUTH_TOKEN:
                super(TwilioLookup, self).check_configuration(configuration)
            else:
                self.log.info("Could not find TWILIO_ACCOUNT_SID or "
                              "TWILIO_AUTH_TOKEN in plugin configuration. ")
                return

        return

    def activate(self):
        if self.config is None:
            self.log.info("TwilioLookup not configured - plugin not "
                          "activating.")
        else:
            self.TWILIO_ACCOUNT_SID = self.config.get('TWILIO_ACCOUNT_SID',
                                                      None)
            self.TWILIO_AUTH_TOKEN = self.config.get('TWILIO_AUTH_TOKEN',
                                                     None)
            if self.TWILIO_ACCOUNT_SID and self.TWILIO_AUTH_TOKEN:
                lookup_client = TwilioLookupsClient(self.TWILIO_ACCOUNT_SID,
                                                    self.TWILIO_AUTH_TOKEN)
                self.lookup_client = lookup_client

                super(TwilioLookup, self).activate()
                self.log.info("Starting TwilioLookup.")
            else:
                self.log.info("Not starting TwilioLookup - could not find "
                              "Twilio credentials in configuration.")

    @botcmd
    def lookup(self, message, args):
        """ Lookup information on a phone number using Twilio Lookup.

        With E.164 formatting:
        !lookup +15108675309

        With local formatting:
        !lookup UK 020 8366 1177


        Lovingly craft by your friendly neighborhood Twilio developer network
        crew.
        """
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
                          "{0}.".format(number.carrier['name'])
            else:
                yield number

    def lookup_e164_number(self, number_string):
        try:
            kwargs = {'include_carrier_info': True}
            return self.lookup_client.phone_numbers.get(number_string,
                                                        **kwargs)
        except TwilioRestException as e:
            return "Could not find information on phone number " \
                   "{0}: {1}".format(number_string, e)

    def sanitize_number(self, number):
        if not any(character.isdigit() for character in number):
            return "Could not find a number here: " \
                   "{0}".format(number)
        if any(character.isalpha() for character in number):
            split = number.split(" ")
            if len(split) > 1 and len(split[0]) == 2:
                number = phonenumbers.parse("".join(split[1:]),
                                            split[0])
            else:
                # Gross hack as PhoneNumberMatcher doesn't support indexing.
                for match in phonenumbers.PhoneNumberMatcher(number, "US"):
                    number = match.number
                    break
        else:
            try:
                number = phonenumbers.parse(number)
            except phonenumbers.phonenumberutil.NumberParseException as e:
                number = phonenumbers.parse(number, "US")

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
