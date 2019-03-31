import subprocess
import re
import sys
import datetime
import time

#time in seconds
sTime = 60 

website = raw_input("Enter website/IP address/hostname to ping ... ")

#ping count for unix systems
num = '4' 

#retrieves operating system type
os = sys.platform 

#Ping command for Windows systems
windows_ping = ['ping', website] 

#Ping command for unix systems
unix_ping = ['ping', website, "-c" "{}".format(num)] 

print("pinging " + website +  "\n") 

while True:
    #if the variable os returns Windows, execute the windows_ping command
    #stdout and stderr redirects data from the ping process to variables output and error respectively
    if os == "Windows" or os == "win32":
        ping = subprocess.Popen (
        windows_ping, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        
    #if os returns Linux or Darwin, execute the unix_ping command
    if os == "linux" or os == "linux2" or os == "Darwin":
        ping = subprocess.Popen (
        unix_ping, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        
    #wait for the ping command to execute completely
    ping.wait()

    #Read output of the ping command captured by subprocess.pipe
    output = ping.stdout.read()
    error = ping.stderr.read()
    
    #Open(or create) a text file called pingtest.txt and ammend it
    sFile = open("pingtest.txt","a")
    
    #write any errors to the new file and print and exit the script
    if error:
        sFile.write(error)
        print(error)
        sys.exit(2)
        
    #variable to retrieve current date and time
    now = datetime.datetime.now()

    sFile.write("\n Pinging " + website + " on " + os + "\n")
    sFile.write(now.strftime("%Y-%m-%d %H:%M:%S" "\n"))
    
    #write output retrieved from subprocess to file
    sFile.write(output)

    #print output on screen
    print(output)
    #print retransmit message
    print("Retransmitting ping in {} minutes".format(sTime/60))
    #snooze time until ping command runs again
    time.sleep(sTime)
    
