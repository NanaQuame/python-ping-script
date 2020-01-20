
"""Test for ping_script_v3.py"""

from __future__ import absolute_import

from absl import app
from absl import flags
from absl.testing import flagsaver

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
FLAGS.report = ('/home/nanaquame/Desktop/coding/ping_dir/'
                    'python-ping-script/mock_data/test_file')

class testPingScript(unittest.TestCase):
  """ Tests for python-ping-script. """

  def setUp(self):
    super(testPingScript, self).setUp()
    self.host = 'amazon.com'
    self.count = 4

    self.fs = fake_fs.FakeFilesystem()
    self.fs_os = fake_fs.FakeOsModule(self.fs)
    self.fs_open = fake_fs.FakeFileOpen(self.fs)

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

  @flagsaver.flagsaver(host='apple.com')
  @mock.patch.object(ping_script_v3, 'os_finder', autospec=True)
  def testPingCommandLinuxCheck(self, mock_os_finder):
    mock_os_finder.return_value = 'linux'
    core = ping_script_v3.ping_script()
    ping_result = core.ping_command(self.host, self.count)

    self.assertIn('ping', ping_result[0])
    self.assertTrue(mock_os_finder.called)

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
    with self.assertRaises(PermissionError):
      core.WriteReport(self.fs_open, success_output, error_output, 
                      report_file)
    self.assertTrue(mock_file_open.called)

  @mock.patch.object(ping_script_v3.ping_script, 'write_file', autospec=True)
  def testReport_FileNotFoundError(self, mock_file_open):
    mock_file_open.side_effect = FileNotFoundError

    report_file = FLAGS.report
    core = ping_script_v3.ping_script()

    success_output, error_output = core.ping_command(self.host, self.count)
    with self.assertRaises(FileNotFoundError):
      core.WriteReport(self.fs_open, success_output, error_output, 
                      report_file)
      self.assertTrue(mock_file_open.called)

  @mock.patch.object(ping_script_v3.ping_script, 'write_file', autospec=True)
  def testReport_IsADirectoryError(self, mock_file_open):
    mock_file_open.side_effect = IsADirectoryError

    report_file = FLAGS.report
    core = ping_script_v3.ping_script()

    success_output, error_output = core.ping_command(self.host, self.count)
    with self.assertRaises(IsADirectoryError):
      core.WriteReport(self.fs_open, success_output, error_output, 
                      report_file)
    self.assertTrue(mock_file_open.called)

  def testReportSuccess(self):
    core = ping_script_v3.ping_script()

    self.fs.create_file('report_file')
    
    success_output, error_output = core.ping_command(self.host, self.count)
    core.write_file(success_output, error_output, 'report_file', self.fs_open)
    
    assert self.fs_os.path.exists('report_file')
    with self.fs_open('report_file', 'r') as read_file:
      read_contents = read_file.read()
    self.assertIn('ping', read_contents)

  @flagsaver.flagsaver(report='test_file')
  def testExecutor(self):
    core = ping_script_v3.ping_script()
    success_output, error_output = core.ping_command(self.host, self.count)
    core.Executor(success_output, error_output, report=False)

if __name__ == '__main__':
  unittest.main(testRunner=HTMLTestRunner(output='python-ping-script'))
