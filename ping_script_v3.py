#!/usr/bin/python3
# Lint as Python3

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import json
import logging
import oses
import os
import subprocess
import sys

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
  """Error storing output to provided path."""


class RpcError(Exception):
  """Error sending/receiving RPC Stream information."""


class UnknownRequest(Exception):
  """Improper request initiated."""


class FileReportError(Exception):
  """Issue with writing to report."""


def os_finder():
  """Check for which operating system this script is running on."""
  os_check = sys.platform

  if (not os_check) or (os_check == None):
    raise ValueError('Unknown OS Type returned.')

  elif os_check in oses.os_list:
      return os_check
  
  else:
    raise ValueError('Incompatible Operating Sytems: %s', os_check)


class ping_script:
  """Based on os, host, count and other parameters, execute the ping script"""
  def __init__(self):
    pass

  def ping_command(self, host, count):
    """Run os_finder function to find out specific os and run command"""

    os_result = os_finder()
    FLAGS(sys.argv)

    if os_result.startswith(('linux2', 'linux', 'Linux', 'Darwin')):
      logging.info('Executing script on a %s system', os_result)
      pingResult = ['ping', host, "-c", "{}".format(count)]

    if os_result.startswith(('Windows', 'Win32')):
      logging.info('Executing script on Windows sys')
      pingResult = ['ping' + host]

    ping_execute = subprocess.Popen(pingResult, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
 
    success_output = ping_execute.stdout.read().decode("utf-8")
    error_output = ping_execute.stderr.read().decode("utf-8")

    if not success_output or error_output:
      raise UnknownRequest('Possibly invalid host address...')

    else:
      return success_output, error_output

  def write_file(self, success_output, error_output, report, open_lib):
    with open_lib(report, 'a') as filer:
        if success_output:
          filer.write(success_output)
        if error_output:
          filer.write(error_output)

  def WriteReport(self, open_lib, success_output, error_output, report):
    logging.info('Writing report to %s...',report)

    try:
      core = ping_script()
      core.write_file(success_output, error_output, report, open_lib)
      logging.info('report write complete...')

    except FileNotFoundError as error_message:
      raise FileNotFoundError('Unable to write to report: %s', error_message)
    except IsADirectoryError as error_message:
      raise IsADirectoryError('Invalid file location: %s', error_message)
    except PermissionError:
      raise PermissionError('No permissions to access this file...')
    # TODO (nanaquame) Implement continuation mechanism if file location not found by printing
    # to STDOUT instead of exiting program.


  def Executor(self, success_output, error_output, report):
    """call all other functions in the script."""
    FLAGS(sys.argv)
    if report:
      core = ping_script()
      core.WriteReport(open, success_output, error_output, report)

    else:
      logging.info('Writing report to stdout...')
      if success_output:
        sys.stdout.write(success_output)
      if error_output:
        sys.stdout.write(error_output)


def main(argv):
  FLAGS(sys.argv)
  core = ping_script()
  success_output, error_output = core.ping_command(FLAGS.host, FLAGS.count)

  core.Executor(success_output, error_output, FLAGS.report)
    
# TODO (nanaquame) Leverage speedtest-cli into this script
# TODO (nanaquame) Implement nmap-cli for additional functionality
# TODO (nanaquame) Add inetutils capabilities like traceroute and others

if __name__ == "__main__":
    app.run(main)
