#!/usr/bin/python
import sys
import platform
import subprocess
import datetime
import time

num = 4
os = platform.system()

host_list = ['google.com',
             'facebook.com',
             'amazon.com',
             'microsoft.com']

def timer():
    for remaining in range(30, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} seconds remaining...".format(remaining))
        sys.stdout.flush()
        time.sleep(1)

while True:
    for host in host_list:
        def log_writer(output, start_time):
            with open("ping_stat.txt", "a") as sFile:
                sFile.write(str(start_time) + "\n")
            with open("ping_stat.txt", "ab") as sFile:
                sFile.write(output)

        def ping():
            start_time = datetime.datetime.now()
            print(start_time)
            print("Testing connectivity to " + host)

            if os == 'Windows' or os =='Win32':
                pingResults = ['ping', host]

            elif [(os == 'Unix') or (os == 'Darwin') 
                  or (os == 'Linux') or (os == 'linux2')]:
                pingResults = ['ping', host, "-c", "{}".format(num)]

            else:
                print("Unknown operatint system")
                sys.exit()

            ping = subprocess.Popen (pingResults, stdout = subprocess.PIPE,
                                     stderr = subprocess.PIPE)

            ping.wait()
            output = ping.stdout.read()
            error = ping.stderr.read()

            print(output)
            log_writer(output, start_time)

            end_time = str(datetime.datetime.now() - start_time)
            print("Elapsed time: " + end_time + "\n")

        while True:
            ping()
            timer()
            break
        continue
