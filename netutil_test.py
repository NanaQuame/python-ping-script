"""Test for netutil.py"""

from absl import app
from absl import flags
from absl.testing import flagsaver
from parameterized import parameterized

from pyfakefs import fake_filesystem as fake_fs
from io import StringIO
import mock
import os
import oses
import netutil
import sys
import unittest

FLAGS = flags.FLAGS
FLAGS.host = 'google.com'
report = ('/mock_data/test_file')

fs = fake_fs.FakeFilesystem()
fs_os = fake_fs.FakeOsModule(fs)
fs_open = fake_fs.FakeFileOpen(fs)

with open('speedtest_report', 'r') as file:
  speedtest_contents = file.read()

with open('traceroute_result', 'r') as file:
  traceroute_content = file.read()

class testPingScript(unittest.TestCase):
  """ Tests for python-ping-script. """

  def setUp(self):
    super(testPingScript, self).setUp()
    self.host = 'google.com'
    self.count = 4

  def test_os_finder_Success(self):
    os_check = netutil.os_finder()
    self.assertIn(os_check, oses.os_list)

  @mock.patch('sys.platform', None)
  def test_os_finder_returnNoneOrEmpty(self):
    with self.assertRaises(netutil.UnknownRequest):
      netutil.ping_command(self.host, self.count)

  @mock.patch('sys.platform', 'AndyOS')
  def test_os_finder_unknownOS(self):
    with self.assertRaises(ValueError):
      netutil.os_finder()

  def testPingCommandWrongHostFormat(self):
    with self.assertRaises(netutil.UnknownRequest):
      netutil.ping_command('youtube.org', self.count)

  @flagsaver.flagsaver(speedtest=False)
  def testReportSuccess(self):
    if fs_os.path.exists(report):
      fs_os.remove(report)
    fs.create_file(report)
    success_output, error_output = netutil.ping_command(self.host, self.count)
    netutil.Executor(success_output, error_output, report, fs_open,
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
    netutil.WriteReport(fs_open, success_output, error_output, report, speedtest_contents, 
                        speedtest_contents, '', self.host)
    with fs_open(report, 'r') as file:
      read_contents = file.read()
    self.assertIn('Name or service not known', read_contents)

  @flagsaver.flagsaver(speedtest=True)
  @flagsaver.flagsaver(report=True)
  def testExecutorSuccess(self):
    fs.create_file(report)
    success_output, error_output = netutil.ping_command(self.host, self.count)
    netutil.Executor(success_output, error_output, report, fs_open,
                     speedtest_contents, '', self.host)
    self.assertTrue(len(report)>1)

  def testGetSpeedTestData(self):
    output = netutil.GetBandwidthData()
    self.assertIn('Download', str(output))
  
  @mock.patch('sys.stdout', new_callable=StringIO)
  def testTraceroute_summary(self, mock_stdout):
    netutil.traceroute_summary(self.host)
    traceroute_strings = ['DNS Lookup', self.host, 'routers', 'round trip time']
    for string in traceroute_strings:
      self.assertIn(string, mock_stdout.getvalue())

  @mock.patch.object(netutil, 'ping_command', autospec=True)
  @mock.patch.object(netutil, 'os_finder', return_value='win32')
  def testWindowsErrorsRaisesException(self, os_mock, ping_mock):
    ping_success = 'could not find host'
    ping_error = ''
    ping_mock.return_value = (ping_success, ping_error)
    with self.assertRaises(netutil.UnknownRequest):
      netutil.Executor(ping_success, ping_error, report=False, open_lib=fs_open,
                       speedtest=speedtest_contents, traceroute='', host=self.host)

  @flagsaver.flagsaver(host='github.com')
  @flagsaver.flagsaver(report=False)
  @flagsaver.flagsaver(speedtest=True)
  @mock.patch('sys.stdout', new_callable=StringIO)
  @mock.patch.object(netutil, 'GetBandwidthData', autospec=True)
  def testWriteReportToStdout(self, mock_bandwidth, mock_stdout):
    mock_bandwidth.return_value = ['Download:80mb', 'Upload:80mb']
    success_output, error_output = netutil.ping_command('linux.com', 5)
    netutil.Executor(success_output, error_output, report=False, open_lib=fs_open,
                     speedtest=speedtest_contents, traceroute='', host=self.host)
    self.assertIn('statistics', mock_stdout.getvalue())

  def tearDown(self):
    super(testPingScript, self).tearDown()
    mock.patch.stopall()


class testWriteReportRaisesExceptions_parameterized(unittest.TestCase):
  def setUp(self):
    super(testWriteReportRaisesExceptions_parameterized, self).setUp()
    self.host = 'google.com'
  
  @parameterized.expand([('PermissionError'), ('FileNotFoundError'), 
                       ('IsADirectoryError')])
  @flagsaver.flagsaver(speedtest=True)
  @flagsaver.flagsaver(host='linux.com')
  @flagsaver.flagsaver(report=True)
  @mock.patch.object(netutil, 'WriteReport', autospec=True)
  @mock.patch.object(netutil, 'GetBandwidthData', return_value=[
    'Download:80mb', 'Upload:80mb'])
  def testWriteReport_(self, exception_value, mock_bandwidth, mock_write_file):
    mock_write_file.side_effect = eval(exception_value)
    if fs_os.path.exists(report):
      fs_os.remove(report)
    fs.create_file(report)

    success_output, error_output = netutil.ping_command('linux.com', 4)
    with self.assertRaises(netutil.FileError):
      netutil.Executor(success_output, error_output, report, fs_open, speedtest_contents, '', self.host)
    self.assertTrue(mock_write_file.called)
  
  def tearDown(self):
    super(testWriteReportRaisesExceptions_parameterized, self).tearDown()
    mock.patch.stopall()


class testpingscript_diff_os(unittest.TestCase):
  def setUp(self):
    super(testpingscript_diff_os, self).setUp()
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

    success_output, error_output = ('packets sent = 4, latency = 6', '')
    netutil.Executor(success_output, error_output, report, fs_open,
                      speedtest_contents, '', self.host)
    with fs_open(report, 'r') as file:
      report_contents = file.read()
    self.assertIn('latency', report_contents)
    self.assertEqual(len(error_output), 0)

  def tearDown(self):
    super(testpingscript_diff_os, self).tearDown()
    mock.patch.stopall()

if __name__ == '__main__':
  unittest.main()
