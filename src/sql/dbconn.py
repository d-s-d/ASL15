import psycopg2
from config import config

connect_str = "host='{hostname}' dbname='{dbname}' user='{username}' password='{password}'".format(**config)

def get_connection():
  conn = psycopg2.connect(connect_str)
  conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
  return conn
