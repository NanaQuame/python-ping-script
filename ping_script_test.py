
"""Test for ping_script_v3.py"""

from __future__ import absolute_import

from absl import app
from absl import flags
from absl.testing import flagsaver
from parameterized import parameterized

from pyfakefs import fake_filesystem as fake_fs
from pyunitreport import HTMLTestRunner

import json
import logging
import mock
import os
import oses
import ping_script_v3
import subprocess
import sys
import time
import unittest

FLAGS = flags.FLAGS
FLAGS.host = 'google.com'
report = ('/home/nanaquame/Desktop/coding/ping_dir/'
          'python-ping-script/mock_data/test_file')

fs = fake_fs.FakeFilesystem()
fs_os = fake_fs.FakeOsModule(fs)
fs_open = fake_fs.FakeFileOpen(fs)

class testPingScript(unittest.TestCase):
  """ Tests for python-ping-script. """

  def setUp(self):
    super(testPingScript, self).setUp()
    self.host = 'amazon.com'
    self.count = 4

  def test_os_finder_Success(self):
    os_check = ping_script_v3.os_finder()
    self.assertIn(os_check, oses.os_list)

  @mock.patch('sys.platform', None)
  def test_os_finder_returnNoneOrEmpty(self):
    with self.assertRaises(ValueError):
      ping_script_v3.os_finder()

  @mock.patch('sys.platform', 'AndyOS')
  def test_os_finder_unknownOS(self):
    with self.assertRaises(ValueError):
      ping_script_v3.os_finder()

  def testPingCommandWrongHostFormat(self):
    core = ping_script_v3.ping_script()
    with self.assertRaises(ping_script_v3.UnknownRequest):
      core.ping_command('youtube.org', self.count)

  @mock.patch.object(ping_script_v3.ping_script, 'write_file', autospec=True)
  def testReport_FilePermission(self, mock_file_open):
    mock_file_open.side_effect = PermissionError

    report_file = FLAGS.report
    core = ping_script_v3.ping_script()

    success_output, error_output = core.ping_command(self.host, self.count)
    with self.assertRaises(ping_script_v3.FileError):
      core.WriteReport(fs_open, success_output, error_output, 
                      report_file)
    self.assertTrue(mock_file_open.called)

  @mock.patch.object(ping_script_v3.ping_script, 'write_file', autospec=True)
  def testReport_FileNotFoundError(self, mock_file_open):
    mock_file_open.side_effect = FileNotFoundError

    report_file = FLAGS.report
    core = ping_script_v3.ping_script()

    success_output, error_output = core.ping_command(self.host, self.count)
    with self.assertRaises(ping_script_v3.FileError):
      core.WriteReport(fs_open, success_output, error_output, 
                      report_file)
      self.assertTrue(mock_file_open.called)

  @mock.patch.object(ping_script_v3.ping_script, 'write_file', autospec=True)
  def testReport_IsADirectoryError(self, mock_file_open):
    mock_file_open.side_effect = IsADirectoryError

    report_file = FLAGS.report
    core = ping_script_v3.ping_script()

    success_output, error_output = core.ping_command(self.host, self.count)
    with self.assertRaises(ping_script_v3.FileError):
      core.WriteReport(fs_open, success_output, error_output, 
                      report_file)
    self.assertTrue(mock_file_open.called)

  def testReportSuccess(self):
    core = ping_script_v3.ping_script()

    fs.create_file('report_file')
    
    success_output, error_output = core.ping_command(self.host, self.count)
    core.write_file(success_output, error_output, 'report_file', fs_open)
    
    assert fs_os.path.exists('report_file')
    with fs_open('report_file', 'r') as read_file:
      read_contents = read_file.read()
    self.assertIn('packets transmitted', read_contents)

  def testReportWritesErrorOutput(self):
    core = ping_script_v3.ping_script()
    fs.create_file(report)
    success_output, error_output = ('', 'ping: youtube.com: Name or ' 
                                      'service not known')
    core.write_file(success_output, error_output, report, fs_open)
    with fs_open(report, 'r') as file:
      contents = file.read()
    self.assertIn('Name or service not known', contents)

  @flagsaver.flagsaver(report='test_file')
  def testExecutor(self):
    core = ping_script_v3.ping_script()
    success_output, error_output = core.ping_command(self.host, self.count)
    core.Executor(success_output, error_output, report=False, open_lib=open)
  
  def tearDown(self):
    super(testPingScript, self).tearDown()
    mock.patch.stopall()

class testpingscript_parameterized(unittest.TestCase):
  def setUp(self):
    super(testpingscript_parameterized, self).setUp()

  @parameterized.expand([('linux', True), ('Win32', True)])
  @flagsaver.flagsaver(host='cisco.com')
  @flagsaver.flagsaver(report=report)
  @mock.patch.object(ping_script_v3, 'os_finder', autospec=True)
  def testPingCommandCheck(self, os_value, report_param, mock_os_finder):
    if fs_os.path.exists(report):
      fs_os.remove(report)

    fs.create_file(report)
    mock_os_finder.return_value = os_value
    core = ping_script_v3.ping_script()
    success_output, error_output = core.ping_command('cisco.com', 4)
    core.Executor(success_output, error_output, report, fs_open)
    self.assertIn('packets transmitted', success_output)
    self.assertEqual(len(error_output), 0)
    self.assertTrue(mock_os_finder.called)

  def tearDown(self):
    super(testpingscript_parameterized, self).tearDown()
    mock.patch.stopall()

if __name__ == '__main__':
  unittest.main(testRunner=HTMLTestRunner(output='python-ping-script'))
