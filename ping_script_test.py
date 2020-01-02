"""Test for ping_script_v3.py"""

from __future__ import absolute_import

from absl import app
from absl import flags
from absl.testing import flagsaver


import json
import logging
import mock
import os
import oses
import ping_script_v3
import pyfakefs
import subprocess
import sys
import time
import unittest

FLAGS = flags.FLAGS

_initial_flag_values = flagsaver.save_flag_values()

host = 'google.com.gh'
report_location = ('/home/nanaquame/Desktop/coding/ping_dir/'
                    'python-ping-script/mock_data')

class testPingScript(unittest.TestCase):
  def setUp(self):
    super(testPingScript, self).setUp()
    # fs = pyfakefs.fake_filesystem
    self.success_output = 'ping successful'
    self.error_output = 'ping failed'

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
  
  def test_Executor(self):
    pass

  # flagsaver._FlagOverrider(host=host)
  # flagsaver._FlagOverrider(report=report_location)
  # @mock.patch.object(ping_script_v3, 'os_finder', autospec=True)
  # def testPingCommand(self, mock_os_finder):
  #   mock_os_finder.return_value = 'linux2'
  #   core = ping_script_v3.ping_script()
  #   core.Executor(open, self.success_output, self.error_output)

  #   self.assertTrue(mock_os_finder.called)
    
if __name__ == '__main__':
  unittest.main()