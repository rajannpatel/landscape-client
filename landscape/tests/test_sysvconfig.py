import mock

from landscape.tests.helpers import LandscapeTest

from landscape.sysvconfig import SysVConfig, ProcessError


class SysVConfigTest(LandscapeTest):

    def test_set_to_run_on_boot(self):
        filename = self.makeFile("RUN=0\n")
        sysvconfig = SysVConfig(filename)
        sysvconfig.set_start_on_boot(True)
        self.assertEqual(file(filename, "r").read(), "RUN=1\n")

    def test_set_to_not_run_on_boot(self):
        filename = self.makeFile("RUN=1\n")
        sysvconfig = SysVConfig(filename)
        sysvconfig.set_start_on_boot(False)
        self.assertEqual(file(filename, "r").read(), "RUN=0\n")

    def test_configured_to_run(self):
        filename = self.makeFile("RUN=1\n")
        sysvconfig = SysVConfig(filename)
        self.assertTrue(sysvconfig.is_configured_to_run())

    def test_not_configured_to_run(self):
        filename = self.makeFile("RUN=0\n")
        sysvconfig = SysVConfig(filename)
        self.assertFalse(sysvconfig.is_configured_to_run())

    def test_blank_line(self):
        filename = self.makeFile("RUN=1\n\n")
        sysvconfig = SysVConfig(filename)
        self.assertTrue(sysvconfig.is_configured_to_run())

    def test_spaces(self):
        filename = self.makeFile(" RUN = 1   \n")
        sysvconfig = SysVConfig(filename)
        self.assertFalse(sysvconfig.is_configured_to_run())

    def test_leading_and_trailing_spaces(self):
        filename = self.makeFile(" RUN=1   \n")
        sysvconfig = SysVConfig(filename)
        self.assertTrue(sysvconfig.is_configured_to_run())

    def test_spaces_in_value(self):
        filename = self.makeFile(" RUN= 1   \n")
        sysvconfig = SysVConfig(filename)
        self.assertFalse(sysvconfig.is_configured_to_run())

    def test_non_integer_run(self):
        filename = self.makeFile("RUN=yesplease")
        sysvconfig = SysVConfig(filename)
        self.assertTrue(sysvconfig.is_configured_to_run())

    @mock.patch("os.system", return_value=0)
    def test_run_landscape(self, system_mock):
        filename = self.makeFile("RUN=1\n")
        sysvconfig = SysVConfig(filename)
        sysvconfig.restart_landscape()
        system_mock.assert_called_once_with(
            "/etc/init.d/landscape-client restart")

    @mock.patch("os.system", return_value=-1)
    def test_run_landscape_with_error(self, system_mock):
        filename = self.makeFile("RUN=1\n")
        sysvconfig = SysVConfig(filename)
        self.assertRaises(ProcessError, sysvconfig.restart_landscape)
        system_mock.assert_called_once_with(
            "/etc/init.d/landscape-client restart")

    @mock.patch("os.system", return_value=0)
    def test_stop_landscape(self, system_mock):
        filename = self.makeFile("RUN=1\n")
        sysvconfig = SysVConfig(filename)
        sysvconfig.stop_landscape()
        system_mock.assert_called_once_with(
            "/etc/init.d/landscape-client stop")

    @mock.patch("os.system", return_value=-1)
    def test_stop_landscape_with_error(self, system_mock):
        filename = self.makeFile("RUN=1\n")
        sysvconfig = SysVConfig(filename)
        self.assertRaises(ProcessError, sysvconfig.stop_landscape)
        system_mock.assert_called_once_with(
            "/etc/init.d/landscape-client stop")
