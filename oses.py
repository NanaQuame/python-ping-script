os_samples = {
            'Linux':['linux', 'linux2'],
            'Windows' : 'win32',
            'Windows/Cygwin' : 'cygwin',
            'Windows/Msys2' : 'msys',
            'Mac OS' : 'darwin',
            'OS/2' : 'os2',
            'OS/2 EMX' : 'osemx',
            'RiscOS' : 'riscos',
            'AtheOS' : 'atheos', 
            'FreeBSD 7': 'freebsd7',
            'FreeBSD 8' : 'freebsd8',
            'FreeBSD N' : 'freebsdN',
            'OpenBSD 6' : 'openbsd6'
            }

os_list = []

def checklist(os_samples):
  for items in os_samples.values():
    if (type(items)) is list:
        for things in items:
          os_list.append(things)
    if (type(items)) is str:
          os_list.append(items)


checklist(os_samples)
