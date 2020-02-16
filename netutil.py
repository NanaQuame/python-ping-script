"""a script that runs ping and speedtest-cli."""

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import json
import logging
import os
import subprocess
import sys

from absl import app
from absl import flags
from hurry.filesize import size, verbose
from prettytable import PrettyTable

import oses

FLAGS = flags.FLAGS

flags.DEFINE_string('host', None, 'host to ping')
flags.DEFINE_integer('count', 4, 'number of icmp packets to send')
flags.DEFINE_string('report', None, 'location to store ping result')

flags.mark_flag_as_required('host')

# TODO (nanaquame) Implement nmap-cli for additional functionality
# TODO (nanaquame) Add inetutils capabilities like traceroute and others

class FileError(Exception):
  """Error storing output to provided path."""


class UnknownRequest(Exception):
  """Improper request initiated."""


def os_finder():
  """Check for which operating system this script is running on."""
  os_check = sys.platform

  if (not os_check) or (os_check is None) or (os_check not in oses.os_list):
    raise ValueError('Unknown OS Type returned.')

  return os_check

def ping_command(host, count):
  """Run os_finder function to find out specific os and run command"""

  os_result = os_finder()
  print(os_result)

  if os_result.startswith(('linux2', 'linux', 'Linux', 'Darwin')):
    logging.info('Executing script on a %s system', os_result)
    pingResult = ['ping', host, "-c", "{}".format(count)]

  if os_result.startswith(('Windows', 'win32')):
    logging.info('Executing script on Windows system')
    pingResult = (f'ping {host} -n {count}')

  ping_execute = subprocess.Popen(pingResult, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)

  success_output = ping_execute.stdout.read().decode("utf-8")
  error_output = ping_execute.stderr.read().decode("utf-8")

  if not success_output or error_output:
    raise UnknownRequest('Unable to complete request. Verify host address.')
  if ('transmit failed' or 'could not find host') in success_output:
    raise UnknownRequest('Incorrect host information on Windows...')

  return success_output, error_output


def GetUploadDownloadSpeed():
  os.system('speedtest --json --secure > speedtest_report')
  with open('speedtest_report') as file:
    data = json.load(file)
  ip = (data['client']['ip'])
  isp = (data['client']['isp'])
  latency = (data['server']['latency'])
  download = size((data['download']), system=verbose)
  upload = size((data['upload']), system=verbose)

  output = PrettyTable()
  output.field_names = [
    'ISP Provider', 'External IP Address', 'Latency', 'Download', 'Upload']
  output.add_row([isp, ip, latency, download, upload])

  return (output)
  
class ping_script:
  """Based on os, host, count and other parameters, execute the ping script
     and write the output to a report file or stdout."""
  def __init__(self):
    pass

  def write_file(self, success_output, error_output, speed, report, open_lib):
    with open_lib(report, 'a') as filer:
        if success_output:
          filer.write(success_output)
        if error_output:
          filer.write(error_output)
        if speed:
          filer.write(speed)

  def WriteReport(self, open_lib, success_output, error_output, report, speed):
    logging.info('Writing report to %s...', report)

    try:
      core = ping_script()
      core.write_file(success_output, error_output, speed, report, open_lib)
      logging.info('report write complete...')

    except (FileNotFoundError, IsADirectoryError, PermissionError) as err:
      raise FileError(f'Unable to write to report to file path. Details: {err}')
    # TODO (nanaquame) Implement continuation mechanism if file location not found by printing
    # to STDOUT instead of exiting program.


def Executor(success_output, error_output, report, open_lib, speed):
  """call all other functions in the script."""
  FLAGS(sys.argv)
  if report:
    core = ping_script()
    core.WriteReport(open_lib, success_output, error_output, report, speed)

  else:
    logging.info('Writing report to stdout...')
    if success_output:
      sys.stdout.write(success_output)
    if error_output:
      sys.stdout.write(error_output)
    if speed:
      sys.stdout.write(speed)


def main(argv):
  FLAGS(sys.argv)
  try:
    success_output, error_output = ping_command(FLAGS.host, FLAGS.count)
    speed_result = str(GetUploadDownloadSpeed())
    Executor(success_output, error_output, FLAGS.report, open, speed_result)
  except (ValueError, FileError, UnknownRequest) as err:
    sys.exit(err)

if __name__ == "__main__":
    app.run(main)
