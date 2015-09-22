#!/usr/bin/env python3

import os, sys

config = {
  'username': 'asl15_mw',
  'dbname': 'asl15',
  'password': 'asl15_mw',
  'hostname': 'localhost',
  'file': 'schema.sql',
}

exec_pre = 'PGPASSWORD={password} psql -h {hostname} {dbname} {username}'
exec_farg = ' --file={file}'

if 'load' in sys.argv:  
  exec_str = (exec_pre + exec_farg).format(**config)
  os.system(exec_str)

if 'login' in sys.argv: 
  exec_str = exec_pre.format(**config)
  os.system(exec_str)
