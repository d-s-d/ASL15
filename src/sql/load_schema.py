#!/usr/bin/env python3

import os, sys
from config import config

exec_pre = 'PGPASSWORD={password} psql -h {hostname} {dbname} {username}'
exec_farg = ' --file={file}'

if 'load' in sys.argv:  
  exec_str = (exec_pre + exec_farg).format(**config)
  os.system(exec_str)

if 'login' in sys.argv: 
  exec_str = exec_pre.format(**config)
  os.system(exec_str)
