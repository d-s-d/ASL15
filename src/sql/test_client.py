#!/usr/bin/env python3

import sys
import psycopg2
from config import config

connect_str = "host='{hostname}' dbname='{dbname}' user='{username}' password='{password}'".format(**config)
try:
  conn = psycopg2.connect(connect_str)
except:
  print("""Could not connect ({0})""".format(connect_str))
  sys.exit(1)

try:
  cur = conn.cursor()
  cur2 = conn.cursor()
  cur.execute("SELECT * FROM register_client()")
  
  cur2.execute("SELECT * FROM register_client()")
  print(cur.fetchall())
  print(cur2.fetchall())
  # client_id = cur.fetchall()[0][0]
 
  #print("Registered Client {0}.".format(client_id)) 
except Exception as e:
  print(e)
  sys.exit(1)
