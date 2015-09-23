
import time
from client import Client

class Queue(object):
  def __init__(self, conn, queue_id=None):
    self.cur = conn.cursor()
    if queue_id is None:
      self.cur.execute("SELECT * FROM create_queue()")
      self.queue_id = self.cur.fetchone()[0]
    else:
      self.cur.execute("SELECT * FROM list_queues()")
      rows = self.cur.fetchall()
      if queue_id == 0:
        raise Exception("illegal queue id: {0}".format(queue_id))
      if queue_id < 0:
        if len(rows) > (-queue_id):
          raise Exception("queue index out of range: {0}".format(queue_id))
        else:
          self.queue_id = rows[-queue_id][0]
      else: 
        if queue_id in map(lambda r: r[0], rows):
          self.queue_id = queue_id
        else:
          raise Exception("queue(id: {0}) does not exist.".format(queue_id))

  def send_message(self, sender, receiver=None, content=None):
    r_id = Client.get_client_id(receiver)
    s_id = sender.client_id
    if content is None:
      content = "{0}".format(time.time())
    self.cur.execute("""SELECT * FROM send_message( 
      %s, %s, %s, %s)""", (self.queue_id, s_id, r_id, content))
    return self.cur.fetchone()

  def exec_op(self, op, receiver, sender=None):
    s_id = Client.get_client_id(sender)
    r_id = receiver.client_id
    q_id = Queue.get_queue_id(self)
    self.cur.execute("SELECT * FROM {0}(%s, %s, %s)".format(op), (r_id, q_id, s_id))
    return self.cur.fetchone()

  def pop(self, receiver, sender=None):
    return self.exec_op("pop", receiver, sender)
  
  def peek(self, receiver, sender=None):
    return self.exec_op("peek", receiver, sender)

  def remove(self):
    self.cur.execute("SELECT * FROM remove_queue(%s)", (self.queue_id, ))
    return self.cur.fetchone()[0]

  def get_queue_id(self):
    if self is None:
      return 0
    return self.queue_id
