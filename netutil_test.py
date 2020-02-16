"""Test for netutil.py"""

from absl import app
from absl import flags
from absl.testing import flagsaver
from parameterized import parameterized

from pyfakefs import fake_filesystem as fake_fs
from pyunitreport import HTMLTestRunner

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
  contents = file.read()

class testPingScript(unittest.TestCase):
  """ Tests for python-ping-script. """

  def setUp(self):
    super(testPingScript, self).setUp()
    self.host = 'amazon.com'
    self.count = 4

  def test_os_finder_Success(self):
    os_check = netutil.os_finder()
    self.assertIn(os_check, oses.os_list)

  @mock.patch('sys.platform', None)
  def test_os_finder_returnNoneOrEmpty(self):
    with self.assertRaises(ValueError):
      netutil.os_finder()

  @mock.patch('sys.platform', 'AndyOS')
  def test_os_finder_unknownOS(self):
    with self.assertRaises(ValueError):
      netutil.os_finder()

  def testPingCommandWrongHostFormat(self):
    with self.assertRaises(netutil.UnknownRequest):
      netutil.ping_command('youtube.org', self.count)

  def testReportSuccess(self):
    core = netutil.ping_script()
    fs.create_file(report)
    success_output, error_output = netutil.ping_command(self.host, self.count)
    core.WriteReport(fs_open, success_output, error_output, report, contents)
    assert fs_os.path.exists(report)
    with fs_open(report, 'r') as read_file:
      read_contents = read_file.read()
    self.assertIn('packets transmitted', read_contents)

  def testReportWritesErrorOutput(self):
    core = netutil.ping_script()
    if fs_os.path.exists(report):
      fs_os.remove(report)
    fs.create_file(report)
    success_output, error_output = ('', 'ping: youtube.com: Name or ' 
                                      'service not known')
    core.WriteReport(fs_open, success_output, error_output, report, contents)
    with fs_open(report, 'r') as file:
      read_contents = file.read()
    self.assertIn('Name or service not known', read_contents)

  @flagsaver.flagsaver(report='test_file')
  def testExecutor(self):
    success_output, error_output = netutil.ping_command(self.host, self.count)
    netutil.Executor(success_output, error_output, report=False, open_lib=open,
                      speed=contents)

  def testGetSpeedTestData(self):
    output = netutil.GetUploadDownloadSpeed()
    self.assertIn('Download', str(output))

  def tearDown(self):
    super(testPingScript, self).tearDown()
    mock.patch.stopall()


class testWriteReportRaisesExceptions_parameterized(unittest.TestCase):
  def setUp(self):
    super(testWriteReportRaisesExceptions_parameterized, self).setUp()
  
  @parameterized.expand([('PermissionError'), ('FileNotFoundError'), 
                       ('IsADirectoryError')])
  @flagsaver.flagsaver(host='linux.com')
  @flagsaver.flagsaver(report=report)
  @mock.patch.object(netutil.ping_script, 'write_file', autospec=True)
  def testWriteReport_(self, exception_value, mock_write_file):
    mock_write_file.side_effect = eval(exception_value)
    report_file = FLAGS.report
    core = netutil.ping_script()

    success_output, error_output = netutil.ping_command('linux.com', 4)
    with self.assertRaises(netutil.FileError):
      core.WriteReport(fs_open, success_output, error_output, 
                      report_file, contents)
    self.assertTrue(mock_write_file.called)
  
  def tearDown(self):
    super(testWriteReportRaisesExceptions_parameterized, self).tearDown()
    mock.patch.stopall()


class testpingscript_diff_os_parameterized(unittest.TestCase):
  def setUp(self):
    super(testpingscript_diff_os_parameterized, self).setUp()

  @parameterized.expand([('linux', True), ('win32', True)])
  @flagsaver.flagsaver(host='cisco.com')
  @flagsaver.flagsaver(report=report)
  @mock.patch.object(netutil, 'os_finder', autospec=True)
  def testPingCommandCheck(self, os_value, report_param, mock_os_finder):
    if fs_os.path.exists(report):
      fs_os.remove(report)
    fs.create_file(report)
    mock_os_finder.return_value = os_value

    success_output, error_output = ('packets sent = 4', '')
    netutil.Executor(success_output, error_output, report, fs_open, contents)
    with fs_open(report, 'r') as file:
      report_contents = file.read()
    self.assertIn('packets', report_contents)
    self.assertEqual(len(error_output), 0)

  def tearDown(self):
    super(testpingscript_diff_os_parameterized, self).tearDown()
    mock.patch.stopall()

if __name__ == '__main__':
  unittest.main(testRunner=HTMLTestRunner(output='python-ping-script'))
