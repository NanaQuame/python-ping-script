# netutil

A script to gather bandwidth information (Download, upload and latency) utilizing speedtest.net CLI tools, provide graphical comparison between local & global speeds, and provides a traceroute summary.

Features:

- Leverages [<https://github.com/sivel/speedtest-cli]> for checking internet bandwdith. Speedtest result outputs information for Internet Service Provider, External IP Address, Latency, Download and upload speeds at the time of execution.
- Provides a graphical comparison of your local speeds (Downloads & Upload) against global averages and the top ten speeds from ranking countries. <https://www.speedtest.net/global-index>. Global speeds are computed on a monthly basis this script is updated accordingly.
- Provides a summary of a traceroute by with:
  - How many routers on the path responded to ICMP (or UDP) packets
  - Utilizes 'getent hosts' to retrieve entries from the databases as specified in your Name Service Switch configuration in /etc/nsswitch.conf. Essentially it performs DNS resolution for the IP responding routers' IP address uziliting your local databases, before consulting DNS resolver if necessary. No need to query your DNS clients if that's not required.

- Accepts parameters for ping(hostname, count, speedtest, tracroute) via CLI flag values.
- Executes on both Unix and Windows systems.

Note: use '--help' on CLI for more information on CLI flags.

Pip Packages to install:

- absl-py <https://pypi.org/project/absl-py/>
- hurry.filesize <https://pypi.org/project/hurry.filesize/>
- prettytable <https://pypi.org/project/PrettyTable/>
- termgraph <https://pypi.org/project/termgraph/>
- speedtest-cli <https://pypi.org/project/speedtest-cli/>

- Provides option to write output of script to report using --report flag during execution.
- Provides robust error-handling at various stages of execution including:
  - Raises value error for undetected/unsupported OS.
    - Verifies that WriteReport method is able to access provided file path location by checking for various os-level errors.
    - Error-handling for when ping_Result does not yield any output (success or error). Generally attributed to invalid hostname or format.

Tests:

- Tests currently cover about 90% of all lines in netutil.py
- Includes parameterized tests to reduce code duplication.

Sample output for: python3 netutil.py --host=4.2.2.2 --speedtest
![Alt text](https://github.com/NanaQuame/python-ping-script/blob/master/speedtest-flag.png "--speedtest sample")

Sample output for: python3 netutil.py --host=4.2.2.2 --traceroute
![Alt text](https://github.com/NanaQuame/python-ping-script/blob/master/traceroute-flag.png "--traceroute sample")
