import os
from landscape.tests.helpers import LandscapeTest

from landscape.manager.keystonetoken import KeystoneToken
from landscape.tests.helpers import ManagerHelper


class KeystoneTokenTest(LandscapeTest):

    helpers = [ManagerHelper]

    def setUp(self):
        super(KeystoneTokenTest, self).setUp()
        self.keystone_file = os.path.join(self.makeDir(), "keystone.conf")
        self.plugin = KeystoneToken(self.keystone_file)

    def test_get_keystone_token_nonexistent(self):
        """
        The plugin provides no data when the keystone configuration file
        doesn't exist.
        """
        self.log_helper.ignore_errors("KeystoneToken: No admin_token found .*")
        self.assertIs(None, self.plugin.get_data())

    def test_get_keystone_token_empty(self):
        """
        The plugin provides no data when the keystone configuration file is
        empty.
        """
        self.log_helper.ignore_errors("KeystoneToken: No admin_token found .*")
        self.makeFile(path=self.keystone_file, content="")
        self.assertIs(None, self.plugin.get_data())

    def test_get_keystone_token_no_admin_token(self):
        """
        The plugin provides no data when the keystone configuration doesn't
        have an admin_token field.
        """
        self.log_helper.ignore_errors("KeystoneToken: No admin_token found .*")
        self.makeFile(path=self.keystone_file, content="[DEFAULT]")
        self.assertIs(None, self.plugin.get_data())

    def test_get_keystone_token(self):
        """
        Finally! Some data is actually there!
        """
        self.makeFile(
            path=self.keystone_file,
            content="[DEFAULT]\nadmin_token = foobar")
        self.assertEqual("foobar", self.plugin.get_data())

    def test_get_keystone_token_non_utf8(self):
        """
        The data can be arbitrary bytes.
        """
        content = "[DEFAULT]\nadmin_token = \xff"
        self.makeFile(
            path=self.keystone_file,
            content=content)
        self.assertEqual("\xff", self.plugin.get_data())

    def test_get_message(self):
        """
        L{KeystoneToken.get_message} only returns a message when the keystone
        token has changed.
        """
        self.makeFile(
            path=self.keystone_file,
            content="[DEFAULT]\nadmin_token = foobar")
        self.plugin.register(self.manager)
        message = self.plugin.get_message()
        self.assertEqual(
            {'type': 'keystone-token', 'data': 'foobar'},
            message)
        message = self.plugin.get_message()
        self.assertIs(None, message)

    def test_resynchronize_message_calls_resynchronize_method(self):
        """
        If the reactor fires a "resynchronize" even the C{_resynchronize}
        method on the ceph plugin object is called.
        """
        self.called = False

        def stub_resynchronize():
            self.called = True
        self.plugin._resynchronize = stub_resynchronize

        self.manager.add(plugin)
        self.reactor.fire("resynchronize")
        self.assertTrue(self.called)
