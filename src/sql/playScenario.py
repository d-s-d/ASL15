#!/usr/bin/env python3

import sys, os, time, inspect
from client import Client
from queue import Queue
from dbconn import get_connection

PREFIX = 'scenario_'

def scenario_simple_producer(queue_name, sender_name, receiver_name, msg_count):
  msg_count = int(msg_count)
  conn = get_connection()
  sender = Client(conn, sender_name)
  receiver = Client(conn, receiver_name)
  queue = Queue(conn, queue_name)

  for i in range(0, msg_count):
    print(sender.send_message(queue, content="{0}, {1}".format(i, time.time()), receiver=receiver))


def scenario_simple_consumer(queue_name, sender_name, receiver_name, msg_count):
  msg_count = int(msg_count)
  conn = get_connection()
  sender = Client(conn, sender_name)
  receiver = Client(conn, receiver_name)
  queue = Queue(conn, queue_name)

  msgs = list()
  for i in range(0, msg_count):
    raw_msg = receiver.pop(queue, sender=sender)
    msgs.append(raw_msg[4])
   
  for msg in msgs:
    splitted_msg = msg.split(', ')
    (i, delay) = (int(splitted_msg[0]), time.time()-float(splitted_msg[1]))
    print("Received message {0} after a delay of {1} seconds.".format(i, delay))

def main():
  scenarios = dict(filter(lambda t: t[0].startswith(PREFIX),
    inspect.getmembers(sys.modules[__name__], inspect.isfunction)))
  scenario_name = sys.argv[1]
  function_name = PREFIX + sys.argv[1]
  args = sys.argv[2:]
  try:
    print("Starting scenario {0} with arguments {1}".format(scenario_name, args))
    scenarios[function_name](*args)
  except KeyError:
    print("ERROR: scenario {0} does not exist.".format(scenario_name))
    print("The following scenarios exist:")
    print('\n'.join(map(lambda s: s[len(PREFIX):], scenarios.keys())))

if __name__=="__main__":
  main()
