#!/usr/bin/python3
# Lint as Python3

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import json
import logging
import os
import subprocess
import sys
import time

from absl import app
from absl import flags

FLAGS = flags.FLAGS

flags.DEFINE_string('host', None, 'Website to ping')
flags.DEFINE_integer('count', 4, 'number of icmp packets to send')
flags.DEFINE_string('report', None, 'location to store ping result')

flags.mark_flag_as_required('host')

class Error(Exception):
  """Container class for exception in this module."""
  pass


class FileError(Exception):
  """Error storing output to provided path"""
  pass


class RpcError(Exception):
  """Error sending/receiving RPC Stream information"""
  pass


def os_finder():
  """Check what operating system this script is running on."""
  try:
   os_type = sys.platform
  except ValueError as error_message:
      logging.error('Not able to determine OS: %s' %error_message)

  return os_type


def countdown_timer():
  """A sleep timer showing a countdown until next execution"""
  for remaining in range(30, 0, -1):
      sys.stdout.write("\r")
      sys.stdout.write("{:2d} seconds remaining...".format(remaining))
      sys.stdout.flush()
      time.sleep(1)


class ping_script:
  """Based on os, host, count and other parameters, execute the ping script"""
  def __init__(self):
    self.host = FLAGS.host
    self.count = FLAGS.count
    self.report = FLAGS.report

  def ping_command(self):
    """Run os_finder function to find out specific os and run command"""
    os_result = os_finder()
    if os_result.startswith(('linux2', 'linux', 'Linux', 'Darwin')):
      logging.info('Executing script on a Linux Workstation')
      pingResult = ['ping', self.host, "-c", "{}".format(self.count)]

    elif os_result.startswith(('Windows', 'Win32')):
      logging.info('Executing script on Windows Rig')
      pingResult = ['ping' + self.host]

    else:
      logging.error('OS Not Found')
      SystemExit(0)

    ping_execute = subprocess.Popen(pingResult, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
    
    success_output = (ping_execute.stdout.read().decode("utf-8"))
    error_output = ping_execute.stderr.read().decode("utf-8")

    return success_output, error_output


  def Executor(self, report, success_output, error_output, open_lib=open):
    if FLAGS.report:
      report = FLAGS.report
      logging.info('Writing report to %s...', report)

      try:
        with open_lib(report, 'a') as filer:
          if success_output:
            filer.write(success_output)
          if error_output:
            filer.write(error_output)

      except FileNotFoundError as error_message:
        logging.error('file not found: %s', error_message)
      except IsADirectoryError as error_message:
        logging.error('Invalid file location: %s', error_message)
      # TODO (nanaquame) Implement continuation mechanism if file location not found by printing
      # to STDOUT instead of exiting program.

    if not report:
      logging.info('Writing report to your stdout...')
      if success_output:
        sys.stdout.write(success_output)
      if error_output:
        sys.stdout.write(error_output)


def main(argv):
  if FLAGS.host:
    report = FLAGS.report
    core = ping_script()

    success_output, error_output = core.ping_command()

    if not success_output or error_output:
      logging.fatal('No value returned from ping outputs')
      SystemExit(1)

    core.Executor(report, success_output, error_output)

# TODO (nanaquame) Leverage speedtest-cli into this script
# TODO (nanaquame) Implement nmap-cli for additional functionality

if __name__ == "__main__":
    app.run(main)
