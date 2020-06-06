# Lint as: python3
"""Tests for netutil."""

import io
import os
import unittest

from absl import flags
from absl.testing import flagsaver
import mock
from parameterized import parameterized
from pyfakefs import fake_filesystem as fake_fs

import netutil

FLAGS = flags.FLAGS
FLAGS.host = 'google.com'
abs_path = '/home/nanaquame/ping_tool/python-ping-script/'
report = ('/mock_data/test_file')

fs = fake_fs.FakeFilesystem()
fs_os = fake_fs.FakeOsModule(fs)
fs_open = fake_fs.FakeFileOpen(fs)

os_list = ['linux', 'linux2', 'win32', 'cygwin', 'msys', 'darwin', 'os2',
           'osemx', 'riscos', 'atheos', 'freebsd7', 'freebsd8', 'freebsdN',
           'openbsd6']

with open(os.path.join(abs_path, 'speedtest_report'), 'r') as file:
  speedtest_contents = file.read()

with open(os.path.join(abs_path, 'traceroute_result'), 'r') as file:
  traceroute_content = file.read()


class TestPingScript(unittest.TestCase):
  """Tests for python-ping-script."""

  def setUp(self):
    super(TestPingScript, self).setUp()
    self.host = 'google.com'
    self.count = 4

  def testOsFinderSuccess(self):
    os_check = netutil.os_finder()
    self.assertIn(os_check, os_list)

  @mock.patch('sys.platform', None)
  def testOsFinderreturnNoneOrEmpty(self):
    with self.assertRaises(netutil.UnknownRequestError):
      netutil.ping_command(self.host, self.count)

  @mock.patch('sys.platform', 'AndyOS')
  def testOsFinderunknownOS(self):
    with self.assertRaises(ValueError):
      netutil.os_finder()

  def testPingCommandWrongHostFormat(self):
    with self.assertRaises(netutil.UnknownRequestError):
      netutil.ping_command('youtube.org', self.count)

  @flagsaver.flagsaver(speedtest=False)
  def testReportSuccess(self):
    if fs_os.path.exists(report):
      fs_os.remove(report)
    fs.create_file(report)
    success_output, error_output = (speedtest_contents, '')
    netutil.executor(success_output, error_output, report, fs_open,
                     speedtest_contents, traceroute_content, self.host)
    with fs_open(report, 'r') as read_file:
      read_contents = read_file.read()
    self.assertIn('statistics', read_contents)

  def testReportWritesErrorOutput(self):
    if fs_os.path.exists(report):
      fs_os.remove(report)
    fs.create_file(report)
    success_output, error_output = ('', 'ping: youtube.com: Name or '
                                    'service not known')
    netutil.write_report(fs_open, success_output, error_output, report,
                        speedtest_contents, speedtest_contents, '', self.host)
    with fs_open(report, 'r') as info:
      read_contents = info.read()
    self.assertIn('Name or service not known', read_contents)

  @flagsaver.flagsaver(speedtest=True)
  @flagsaver.flagsaver(report=True)
  def testExecutorSuccess(self):
    fs.create_file(report)
    success_output, error_output = (speedtest_contents, '')
    netutil.executor(success_output, error_output, report, fs_open,
                     False, False, self.host)
    self.assertGreater(len(report), 1)

  def testGetSpeedTestData(self):
    output = netutil.get_bandwidth_data()
    speedtest_strings = ['Download', 'ISP', 'Local speed', 'Latency']
    for string in speedtest_strings:
      self.assertIn(string, str(output))

  @mock.patch('sys.stdout', new_callable=io.StringIO)
  def testTraceroute_summary(self, mock_stdout):
    netutil.traceroute_summary(self.host)
    traceroute_strings = ['IP Address', 'DNS resolution', 'routers']
    for string in traceroute_strings:
      self.assertIn(string, mock_stdout.getvalue())

  @mock.patch.object(netutil, 'ping_command', autospec=True)
  @mock.patch.object(netutil, 'os_finder', autospec=True)
  def testWindowsErrorsRaisesException(self, os_mock, ping_mock):
    ping_success = 'could not find host'
    ping_error = ''
    ping_mock.return_value = (ping_success, ping_error)
    os_mock.return_value = 'win32'

    with self.assertRaises(netutil.UnknownRequestError):
      netutil.executor(
          ping_success,
          ping_error,
          report=False,
          open_lib=fs_open,
          speedtest=speedtest_contents,
          traceroute='',
          host=self.host)

  @mock.patch('sys.stdout', new_callable=io.StringIO)
  @mock.patch.object(netutil, 'get_bandwidth_data', autospec=True)
  def testwrite_reportToStdout(self, mock_bandwidth, mock_stdout):
    mock_bandwidth.return_value = ['Download:80mb', 'Upload:80mb']
    success_output, error_output = (speedtest_contents, '')
    netutil.executor(
        success_output,
        error_output,
        report=False,
        open_lib=fs_open,
        speedtest=speedtest_contents,
        traceroute='',
        host=self.host)
    output_strings = ['ping', 'download', 'upload', 'isp', 'host', 'latency']
    for string in output_strings:
      self.assertIn(string, mock_stdout.getvalue())


  def tearDown(self):
    super(TestPingScript, self).tearDown()
    mock.patch.stopall()


class Testwrite_reportRaisesExceptionsParameterized(unittest.TestCase):

  def setUp(self):
    super(Testwrite_reportRaisesExceptionsParameterized, self).setUp()
    self.host = 'google.com'

  @parameterized.expand([('PermissionError'), ('FileNotFoundError'),
                         ('IsADirectoryError')])
  @flagsaver.flagsaver(speedtest=True)
  @flagsaver.flagsaver(host='linux.com')
  @flagsaver.flagsaver(report=True)
  @mock.patch.object(netutil, 'write_report', autospec=True)
  @mock.patch.object(
      netutil,
      'get_bandwidth_data',
      return_value=['Download:80mb', 'Upload:80mb'])
  def testwrite_report_(self, exception_value, mock_bandwidth, mock_write_file):
    mock_write_file.side_effect = eval(exception_value)
    if fs_os.path.exists(report):
      fs_os.remove(report)
    fs.create_file(report)
    success_output, error_output = (speedtest_contents, '')
    with self.assertRaises(netutil.FileError):
      netutil.executor(success_output, error_output, report, fs_open,
                       speedtest_contents, '', self.host)
    self.assertTrue(mock_write_file.called)
    self.assertTrue(mock_bandwidth.called)

  def tearDown(self):
    super(Testwrite_reportRaisesExceptionsParameterized, self).tearDown()
    mock.patch.stopall()


class TestPingScriptDifferentOs(unittest.TestCase):

  def setUp(self):
    super(TestPingScriptDifferentOs, self).setUp()
    self.host = 'google.com'

  @parameterized.expand([('linux', True), ('win32', True)])
  @flagsaver.flagsaver(speedtest=True)
  @flagsaver.flagsaver(host='cisco.com')
  @flagsaver.flagsaver(report=True)
  @mock.patch.object(netutil, 'os_finder', autospec=True)
  def testPingCommandCheck(self, os_value, report_param, mock_os_finder):
    if fs_os.path.exists(report):
      fs_os.remove(report)
    fs.create_file(report)
    mock_os_finder.return_value = os_value

    success_output, error_output = (speedtest_contents, '')
    netutil.executor(success_output, error_output, report_param, fs_open,
                     speedtest_contents, '', self.host)
    with fs_open(report, 'r') as info:
      report_contents = info.read()
    self.assertIn('latency', report_contents)
    self.assertEqual(len(error_output), 0)

  def tearDown(self):
    super(TestPingScriptDifferentOs, self).tearDown()
    mock.patch.stopall()

if __name__ == '__main__':
  unittest.main()