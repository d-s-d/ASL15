#!/usr/bin/env python3

import sys, os
from dbconn import get_connection
from client import Client
from queue import Queue

class BehaviorSimpleProducer(object):
  def __init__(self, conn):
    self.conn = conn

  def setup():
    self.c1 = Client(conn)
    self.q1 = Queue(conn)

  def run():
    for i in range(1, 100000):
      self.c1.send_message(self.q1)

def behavior_produce_messages_A(conn):
  c1 = Client(conn)
  q1 = Queue(conn)

def main():
  

if __name__=="__main__":
  main()
