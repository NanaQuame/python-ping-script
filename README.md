# netutils
A script to ping a host, test bandwidth (upload/download) with option to write output to a report. 

Features:
- Accepts parameters for ping(hostname, count) via CLI flag values.
- Ping host for Windows or Unix based systems.
- Leverages [https://github.com/sivel/speedtest-cli] for testing internet bandwdith. Speedtest result outputs information for ISP Provider, External IP Address, Latency, Download and upload speeds at the time of execution.

Note: To use speedtest functionality, make sure to install speedtest-cli tool.

- Provides option to write output of script to report using --report flag during execution.
- Provides robust error-handling at various stages of execution including:
    a. Raises value error for undetected/unsupported OS.
    b. Verifies that WriteReport method is able to access provided file path   location by checking for various os-level errors.
    c. Error-handling for when ping_Result does not yield any output (success or error). Generally attributed to invalid hostname or format.

Tests:
- Tests currently cover about 90% of all lines in netutil.py
- Includes parameterized tests to reduce code duplication.
