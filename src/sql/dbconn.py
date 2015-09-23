import psycopg2
from config import config

connect_str = "host='{hostname}' dbname='{dbname}' user='{username}' password='{password}'".format(**config)

def get_connection():
  return psycopg2.connect(connect_str)
