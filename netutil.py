# Lint as: python3
"""A script to gather bandwidth information (Download, upload and latency).

It utilizes speedtest.net CLI tools, provide graphical comparison between local
& global speeds, and provides a traceroute summary.
"""
import csv
import ipaddress
import json
import logging
import os
import subprocess
import sys
from typing import Tuple

from absl import app
from absl import flags
from prettytable import PrettyTable

FLAGS = flags.FLAGS

flags.DEFINE_string('host', 'google.com', 'host to ping')
flags.DEFINE_integer('count', 10, 'number of icmp packets to send')
flags.DEFINE_string('report', None, 'location to store ping result')
flags.DEFINE_boolean('speedtest', False,
                     'run speedtest-cli and display comparison chart')
flags.DEFINE_boolean('traceroute', False,
                     'run traceroute on host and provide summary of result')

# TODO(nanaquame) Implement nmap-cli for additional functionality
# TODO(nanaquame) Add inetutils capabilities like traceroute and others

os_list = ['linux', 'linux2', 'win32', 'cygwin', 'msys', 'darwin', 'os2',
           'osemx', 'riscos', 'atheos', 'freebsd7', 'freebsd8', 'freebsdN',
           'openbsd6']

class FileError(Exception):
  """Error storing output to provided path."""


class UnknownRequestError(Exception):
  """Improper request initiated."""


def os_finder() -> str:
  """Check for which operating system this script is running on.

  Returns:
    os_check: output of sys.platform.
  Raises:
    ValueError: if sys.platform returns no or unsupported os.
  """
  os_check = sys.platform

  if (not os_check) or (os_check is None) or (os_check not in os_list):
    raise ValueError('Unknown OS Type returned.')

  return os_check


def bytes_to_megabytes(speed_in_bytes: float) -> int:
  """Converts bytes to megabytes.

  Args:
    speed_in_bytes: bandwidth data in bytes
  Returns:
    bytes converted to megabytes.
  """
  return round(speed_in_bytes * 0.000001)


def ping_command(host: str, count: int) -> Tuple[str, str]:
  """Runs ping command for the specific os returned.

  Args:
    host: the host address to ping.
    count: number of times to send the ping request.

  Returns:
    success_error: output of a successful ping.
    error_output: output of an unsuccessful ping.
  Raises:
    UnknownRequestError: If neither success_error or error_output.
  """
  try:
    os_result = os_finder()
  except ValueError as err:
    raise UnknownRequestError(err)

  if os_result.startswith(('linux2', 'linux', 'Linux', 'darwin')):
    logging.info('Executing script on a unix system')
    ping_result = ['ping', host, '-q', '-c', '{}'.format(count)]

  if os_result.startswith(('Windows', 'win32')):
    logging.info('Executing script on Windows system')
    ping_result = (f'ping {host} -n {count}')

  ping_execute = subprocess.Popen(ping_result, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
  ping_execute.wait()

  success_output = ping_execute.stdout.read().decode('utf-8')
  error_output = ping_execute.stderr.read().decode('utf-8')

  if not success_output or error_output:
    raise UnknownRequestError(
        'Request incomplete. Verify host address and connection.')

  return success_output, error_output


def get_bandwidth_data() -> Tuple[str, str]:
  """Run speedtest-cli tool for Various bandwidth and ISP information.

  Returns:
     output: A prettytable object showing ISP Provider, External IP Address,
             Latency, Download and Upload.
  """
  logging.info('Starting speedtest-cli...')
  os.system('speedtest-cli --json --secure > speedtest_report')
  with open('speedtest_report') as file:
    data = json.load(file)
  ip = data['client']['ip']
  isp = data['client']['isp']
  latency = data['server']['latency']
  download = bytes_to_megabytes(data['download'])
  upload = bytes_to_megabytes(data['upload'])

  bandwidth_output = PrettyTable()
  bandwidth_output.field_names = [
      'ISP', 'Public IP Address', 'Latency ⬌', 'Download ⬇', 'Upload ⬆']
  bandwidth_output.add_row([isp, ip, (f'{latency} ms'), (str(download) + ' Mbps'), (str(upload) + ' Mbps')])

  with open('graph_content.csv', 'w+') as file:
    writer = csv.writer(file)

    writer.writerow(['Local speed', download, upload])
    writer.writerow(['Global Average', 74, 39])
    writer.writerow(['Singapore', 198, 207])
    writer.writerow(['Hong Kong', 176, 172])
    writer.writerow(['Thailand', 159, 125])
    writer.writerow(['Switzerland', 152, 97])
    writer.writerow(['Romania', 151, 110])
    writer.writerow(['Monaco', 140, 79])
    writer.writerow(['Andora', 139, 148])
    writer.writerow(['Macau', 137, 127])
    writer.writerow(['Sweden', 137, 109])
    writer.writerow(['Denmark', 136, 105])

  (os.system('termgraph --title " Speedtest comparison as of April 2020 \n'
  '   Keys: Identifier: Download, Upload \n All speeds are measured in M/bits" '
  'graph_content.csv > speed_comparison_graph'))

  with open('speed_comparison_graph', 'r') as file:
    speed_comparison_graph = file.read()

  return str(bandwidth_output), str(speed_comparison_graph)


def traceroute_summary(host: str) -> str:
  """Runs tracroute and generates a summarization.

  Args:
    host: a string of the host to run traceroute against.

  Returns:
    a logging/print output.
  """
  if 'darwin' in sys.platform:
    logging.info(
        'Traceroute summarization not available on MacOS at the moment.')
    return ''
  logging.info(f'starting traceroute to {host}...')
  os.system(f'traceroute {host} > traceroute_result')

  round_trip_times = []
  responding_routers = 0
  non_responding_routers = 0
  list_of_responding_routers = []
  ip_of_host = ''

  with open('traceroute_result', 'r') as file:
    content = file.readlines()

  logging.info('Generating traceroute summary and Name Server resoltuion...')
  for counter, line in enumerate(content):
    if counter == 0:
      ip_retriever = line.split(' ')
      is_valid_ip = ip_retriever[3].strip('(),')
      if ipaddress.ip_address(is_valid_ip): ip_of_host += is_valid_ip
      continue

    if '*' in line:
      non_responding_routers += 1
      continue

    split_traceroute_line = line.split(' ')
    update_split_line = list(filter(None, split_traceroute_line))
    list_of_responding_routers.append(update_split_line[1])
    responding_routers += 1

    for rtt in update_split_line:
      try:
        round_trip_times.append(float(rtt))
      except ValueError:
        continue
    
    average_round_trip_time = round(
        sum(round_trip_times) / len(round_trip_times), 2)

  print(
      f'\nDNS Lookup for {host} returned {ip_of_host} as destination address.\n'
      f'{responding_routers} responding router(s) on this path '
      f'with an average round trip time of {average_round_trip_time} ms\n')

  print(
      'IP address to Name Server mapping for responding routers on the path\n')

  dns_table = PrettyTable()
  dns_table.field_names = ['IP Address', 'DNS resolution']

  for router in list_of_responding_routers:
    os.system(f'getent hosts {router} > dns_table_build')
    with open('dns_table_build', 'r') as file:
      table_content = file.readlines()

    for line in table_content:
      split_dns_info = line.split()
      if not isinstance(split_dns_info[1], int):
        dns_table.add_row([router, split_dns_info[1]])
        dns_table.add_row(['', ''])

  print(dns_table)

  return ''


def write_report(open_lib, success_output: str, error_output: str, report: str,
                 local_speed: str, global_speed: str, traceroute: None,
                 host: str) -> None:
  """Open report location to write report to file path or write.

  Args:
    open_lib: library for opening file. Used for testing.
    success_output: successful output from ping command.
    error_output: error output from ping command (if any)
    report: file path for writing output from commands.
    local_speed: result of speedtest-cli
    global_speed: global speeds from speedtest index.
    traceroute: run traceroute on host and provide summar of output.
    host: host information (FQDN or IP Address)
  """
  with open_lib(report, 'a') as filer:
    sys.stdout.write('--------------------------------------------------------'
                     '-----------------------------\n')
    if success_output:
      filer.write(success_output)
    if error_output:
      filer.write(error_output)
    if local_speed:
      filer.write(local_speed)
    if global_speed:
      filer.write(global_speed)
    if traceroute:
      filer.write(traceroute_summary(host))
  logging.info('Writing report to: %d', report)

  # TODO(nanaquame) Implement continuation mechanism if file location not found
  # by printing to STDOUT instead of exiting program.


def executor(success_output: str, error_output: str, report: str, open_lib,
             speedtest: str, traceroute: None, host: str) -> None:
  """call all other functions in the script.

  Args:
    success_output: successful output from ping command.
    error_output: error output from ping command (if any)
    report: file path for writing output from commands.
    open_lib: library for opening file. Used for testing.
    speedtest: speedtest output to write
    traceroute: traceroute summary.
    host: host information (FQDN or IP Address)

  Raises:
    FileError: If OS error during file access to write report.
    UnknownRequestError: For Windows, a failed ping due to invalid host
    information will still be sent to success_output. Check for strings
    referencingfailed pings instead of proceeding as usual.
  """
  FLAGS(sys.argv)
  windows_errors = ['could not find host', 'transmit failed']
  for error in windows_errors:
    if error in success_output:
      raise UnknownRequestError(
          'Unable to complete request. Verify host address.')

  if speedtest:
    local_speed, global_speeds = get_bandwidth_data()
  else:
    local_speed, global_speeds = '', ''

  if report:
    logging.info('writing report to %d', report)
    try:
      write_report(open_lib, success_output, error_output, report, local_speed,
                   global_speeds, traceroute, host)
    except (FileNotFoundError, IsADirectoryError, PermissionError) as err:
      raise FileError(f'Unable to write to report to file path. Details: {err}')

  else:
    logging.info('Writing report to stdout...')
    sys.stdout.write('-------------------------------------------------------'
                     '------------------------------\n')
    if success_output:
      sys.stdout.write(success_output)
    if error_output:
      sys.stdout.write(error_output)
    if speedtest:
      sys.stdout.write(local_speed)
      sys.stdout.write('\n')
      sys.stdout.write(global_speeds)
      sys.stdout.write('\n')
    if traceroute:
      sys.stdout.write(traceroute_summary(host))


def main(argv):
  logging.info(os.getcwd())
  if len(argv) > 1:
    raise app.UsageError('Too many command-line arguments.')
  FLAGS(sys.argv)
  try:
    success_output, error_output = ping_command(FLAGS.host, FLAGS.count)
    executor(success_output, error_output, FLAGS.report, open, FLAGS.speedtest,
             FLAGS.traceroute, FLAGS.host)
  except (ValueError, FileError, UnknownRequestError) as err:
    sys.exit(err)
  logging.info('Script execution complete!')

if __name__ == '__main__':
  app.run(main)