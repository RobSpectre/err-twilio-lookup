import logging

from unittest.mock import patch
from unittest.mock import Mock

from errbot.backends.test import FullStackTest

from twilio.rest.exceptions import TwilioRestException

config = {
    'TWILIO_ACCOUNT_SID': 'ACxxxxx',
    'TWILIO_AUTH_TOKEN': 'yyyyyyyy'
}


def create_mock_json(path):
    with open(path) as f:
        resp = Mock()
        resp.content = f.read()
        return resp


class TestTwilioLookup(FullStackTest):
    def setUp(self, extra_plugin_dir='.', logging_level=logging.INFO):
        super(TestTwilioLookup, self).setUp(extra_plugin_dir=extra_plugin_dir,
                                            loglevel=logging_level)

        self.bot.set_plugin_configuration('TwilioLookup', config)
        self.bot.activate_plugin('TwilioLookup')

        self.plugin = self.bot.get_plugin_obj_by_name('TwilioLookup')

    def assertCommand(self, command, response, timeout=5):
        self.bot.push_message(command)
        self.assertIn(response, self.bot.pop_message(timeout),
                      "Did not find expected response to command "
                      "{0}: {1}".format(command, response))


class TestTwilioLookupCommands(TestTwilioLookup):
    @patch("twilio.rest.resources.base.make_twilio_request")
    def test_lookup(self, request):
        response = create_mock_json(
            "tests/resources/phone_number_instance.json"
        )

        request.return_value = response

        self.assertCommand('!lookup +15108675309',
                           'I found a US mobile number (510) 867-5309.')
        request.assert_called_with('GET',
                                   'https://lookups.twilio.com/v1'
                                   '/PhoneNumbers/+15108675309',
                                   auth=('ACxxxxx', 'yyyyyyyy'),
                                   params={'Type': 'carrier'},
                                   use_json_extension=False)

    @patch("twilio.rest.resources.base.make_twilio_request")
    def test_lookup_with_country_code(self, request):
        response = create_mock_json(
            "tests/resources/phone_number_instance.json"
        )

        request.return_value = response

        self.assertCommand('!lookup (510)867-5309 US',
                           'I found a US mobile number (510) 867-5309.')
        request.assert_called_with('GET',
                                   'https://lookups.twilio.com/v1'
                                   '/PhoneNumbers/+15108675309',
                                   auth=('ACxxxxx', 'yyyyyyyy'),
                                   params={'Type': 'carrier'},
                                   use_json_extension=False)

    @patch("twilio.rest.resources.base.make_twilio_request")
    def test_lookup_with_twilio_number(self, request):
        response = create_mock_json(
            "tests/resources/phone_number_instance_twilio.json"
        )

        request.return_value = response

        self.bot.push_message("!lookup +15108675309")
        self.bot.pop_message()
        self.assertIn("Twilio", self.bot.pop_message())
        request.assert_called_with('GET',
                                   'https://lookups.twilio.com/v1'
                                   '/PhoneNumbers/+15108675309',
                                   auth=('ACxxxxx', 'yyyyyyyy'),
                                   params={'Type': 'carrier'},
                                   use_json_extension=False)

    @patch("twilio.rest.resources.base.make_twilio_request")
    def test_lookup_with_crap_input(self, request):
        response = create_mock_json(
            "tests/resources/phone_number_instance_twilio.json"
        )

        request.return_value = response

        self.bot.push_message("!lookup Hey there - can you look up"
                              " (510) 8675309?")
        self.bot.pop_message()
        self.assertIn("Twilio", self.bot.pop_message())
        request.assert_called_with('GET',
                                   'https://lookups.twilio.com/v1'
                                   '/PhoneNumbers/+15108675309',
                                   auth=('ACxxxxx', 'yyyyyyyy'),
                                   params={'Type': 'carrier'},
                                   use_json_extension=False)

    @patch("twilio.rest.resources.base.make_twilio_request")
    def test_lookup_handle_rest_error(self, request):
        def raiseException(*args, **kwargs):
            raise TwilioRestException("Test error.", "/error")

        request.side_effect = raiseException

        self.bot.push_message("!lookup +15108675309")

        self.assertIn("Could not find information on phone number",
                      self.bot.pop_message())


class TestTwilioLookupUtilities(TestTwilioLookup):
    @patch("twilio.rest.resources.base.make_twilio_request")
    def test_lookup_164_number(self, request):
        response = create_mock_json(
            "tests/resources/phone_number_instance.json"
        )

        expected = "(510) 867-5309"

        request.return_value = response

        result = self.plugin.lookup_e164_number("+15108675309")
        request.assert_called_with('GET',
                                   'https://lookups.twilio.com/v1'
                                   '/PhoneNumbers/+15108675309',
                                   auth=('ACxxxxx', 'yyyyyyyy'),
                                   params={'Type': 'carrier'},
                                   use_json_extension=False)
        self.assertEquals(expected, result.national_format)

    def test_sanitize_number_e164(self):
        expected = "+15108675309"
        result = self.plugin.sanitize_number(expected)

        self.assertEquals(1, result.country_code)
        self.assertEquals(5108675309, result.national_number)

    def test_sanitize_number_with_country_code(self):
        expected = "(510)867-5309 US"
        result = self.plugin.sanitize_number(expected)
        self.assertEquals(1, result.country_code)
        self.assertEquals(5108675309, result.national_number)

    def test_sanitize_number_not_valid(self):
        expected = "This number is not valid: Country Code: 1 National " \
                   "Number: 5556667777"
        result = self.plugin.sanitize_number("+15556667777")
        self.assertEquals(expected, result)

    def test_sanitize_number_not_possible(self):
        expected = "This number is not possible: Country Code: 1 National " \
                   "Number: 555666777"
        result = self.plugin.sanitize_number("+1555666777")
        self.assertEquals(expected, result)

    def test_sanitize_number_no_digits(self):
        expected = "Could not find a number here: error"
        result = self.plugin.sanitize_number("error")
        self.assertEquals(expected, result)


class TestTwilioLookupWithoutConfiguration(FullStackTest):
    def setUp(self, extra_plugin_dir='.', logging_level=logging.INFO):
        super(TestTwilioLookupWithoutConfiguration,
              self).setUp(extra_plugin_dir=extra_plugin_dir,
                          loglevel=logging_level)

    def test_no_configuration(self):
        plugin_list = self.bot.get_all_active_plugin_names()
        self.assertFalse("TwilioLookup" in plugin_list)

    def test_wrong_configuration(self):
        incomplete_configuration = {"TWILIO_ACCOUNT_SID": "ACxxxx"}
        self.bot.set_plugin_configuration('TwilioLookup',
                                          incomplete_configuration)
        self.bot.activate_plugin('TwilioLookup')

        plugin_list = self.bot.get_all_active_plugin_names()
        self.assertFalse("TwilioLookup" in plugin_list)
