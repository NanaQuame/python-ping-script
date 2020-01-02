import json
import sys
import oses

os_type = sys.platform

if os_type in oses.os_list:
  print(os_type)

else:
  print('os not found: %s', os_type)
  