#!/usr/bin/python
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


class FileError(Exception):
  """Error storing output to provided path"""


class RpcError(Exception):
  """Error sending/receiving RPC Stream information"""

def os_finder():
  """Check what operating system this script is running on."""
  try:
   os_type = sys.platform
  except ValueError as e:
      logging.error('Not able to determine OS: %s' %e)

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
      sys.exit()

    ping_execute = subprocess.Popen(pingResult, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
    
    output = (ping_execute.stdout.read().decode("utf-8"))
    error = ping_execute.stderr.read()

    if output:
      print(output)
    if error:
      print(error)


def main(argv):
  if FLAGS.host:
    logging.info('initiating a ping to %s' %FLAGS.host)
    core = ping_script()
    core.ping_command()

if __name__ == "__main__":
    app.run(main)
