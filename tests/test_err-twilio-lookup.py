from errbot.backends.test import testbot
from errbot import plugin_manager


class TestTwilioLookup(object):
    extra_plugin_dir = '.'

    def setUp(self):
        self.plugin = plugin_manager.get_plugin_obj_by_name('TwilioLookup')

    def test_lookup(self, testbot):
        expected = "test"
        self.bot.push_message("!lookup")

        self.assertTrue(expected in self.bot.pop_message(),
                        "Did not get message 'test', instead: "
                        "{0}".format(self.bot.pop_message()))
