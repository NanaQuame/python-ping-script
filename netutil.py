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
flags.DEFINE_boolean('speedtest', False, 'run speedtest-cli')

flags.mark_flag_as_required('host')

# TODO (nanaquame) Implement nmap-cli for additional functionality
# TODO (nanaquame) Add inetutils capabilities like traceroute and others

class FileError(Exception):
  """Error storing output to provided path."""


class UnknownRequest(Exception):
  """Improper request initiated."""


def os_finder():
  """Check for which operating system this script is running on.
     Returns:
      os_check: output of sys.platform

     Raises:
      ValueError: if sys.platform returns no or unsupported os.
  """
  os_check = sys.platform

  if (not os_check) or (os_check is None) or (os_check not in oses.os_list):
    raise ValueError('Unknown OS Type returned.')

  return os_check

def ping_command(host, count):
  """Runs ping command for the specific os returned. 
    
     Args:
      host: the host address to ping.
      count: number of times to send the ping request.
    
     Returns:
      success_error: output of a successful ping.
      error_output: output of an unsuccessful ping.

     Raises:
      UnknownRequest: If neither success_error or error_output. For Windows, 
                      a failed ping due to invalid host information will still
                      be sent to success_output. Check for strings referencing
                      failed pings instead of proceeding as usual.
  """

  os_result = os_finder()

  if os_result.startswith(('linux2', 'linux', 'Linux', 'darwin')):
    logging.info('Executing script on a %s system', os_result)
    pingResult = ['ping', host, "-c", "{}".format(count)]

  if os_result.startswith(('Windows', 'win32')):
    logging.info('Executing script on Windows system')
    pingResult = (f'ping {host} -n {count}')

  ping_execute = subprocess.Popen(pingResult, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)

  success_output = ping_execute.stdout.read().decode("utf-8")
  error_output = ping_execute.stderr.read().decode("utf-8")

  windows_errors = ['could not find host', 'transmit failed']

  if not success_output or error_output:
    raise UnknownRequest('Request incomplete. Verify host address and connection.')
  for error in windows_errors:
    if error in success_output:
      raise UnknownRequest('Unable to complete request. Verify host address.')

  return success_output, error_output


def GetUploadDownloadSpeed():
  """Run speedtest-cli tool for Various bandwidth and ISP information.
     Returns:
       output: A prettytable object showing ISP Provider, External IP Address,
               Latency, Download and Upload.
  """
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
    'ISP Provider', 'External IP Address', 'Latency ⬌', 'Download ⬇', 'Upload ⬆']
  output.add_row([isp, ip, latency, download, upload])

  return (output)


def WriteReport(open_lib, success_output, error_output, report, speed):
  """Open report location to write report to file path or write.
      Args:
        success_output: successful output from ping command.
        error_output: error output from ping command (if any)
        speed: speedtest output to write
        report: file path for writing output from commands.
        open_lib: library for opening file. Used for testing.
  """
  with open_lib(report, 'a') as filer:
    if success_output:
      filer.write(success_output)
    if error_output:
      filer.write(error_output)
    if speed:
      filer.write(speed)
  logging.info(f'report written to {report}')

  # TODO (nanaquame) Implement continuation mechanism if file location not found by printing
  # to STDOUT instead of exiting program.


def Executor(success_output, error_output, report, open_lib, speedtest):
  """call all other functions in the script.
     
     Args:
      success_output: successful output from ping command.
      error_output: error output from ping command (if any)
      speed: speedtest output to write
      report: file path for writing output from commands.
      open_lib: library for opening file. Used for testing.
     
     Raises:
      FileError: If OS error during file access to write report.
  """
  FLAGS(sys.argv)
  if speedtest:
    speed = str(GetUploadDownloadSpeed())
  else:
    speed = ''

  if report:
    logging.debug(f'writing report to {report}')
    try:
      WriteReport(open_lib, success_output, error_output, report, speed)
    except (FileNotFoundError, IsADirectoryError, PermissionError) as err:
      raise FileError(f'Unable to write to report to file path. Details: {err}')

  else:
    logging.info('Writing report to stdout...')
    if success_output:
      sys.stdout.write(success_output)
    if error_output:
      sys.stdout.write(error_output)
    if speedtest:
      sys.stdout.write(speed)


def main(argv):
  FLAGS(sys.argv)
  try:
    success_output, error_output = ping_command(FLAGS.host, FLAGS.count)
    Executor(success_output, error_output, FLAGS.report, open, FLAGS.speedtest)
  except (ValueError, FileError, UnknownRequest) as err:
    sys.exit(err)

if __name__ == "__main__":
    app.run(main)
