
import time
from client import Client

class Queue(object):
  def __init__(self, conn, name=None):
    self.conn = conn
    cur = conn.cursor()
    if name is None:
      cur.execute("SELECT * FROM create_queue(null)")
    else:
      cur.execute("SELECT * FROM create_queue(%s)", (name, ))
    self.queue_id = cur.fetchone()[0]
    cur.close()

  def send_message(self, sender, receiver=None, content=None):
    r_id = Client.get_client_id(receiver)
    s_id = sender.client_id
    cur = self.conn.cursor()
    if content is None:
      content = "{0}".format(time.time())
    cur.execute("""SELECT * FROM send_message( 
      %s, %s, %s, %s)""", (self.queue_id, s_id, r_id, content))
    msg = cur.fetchone()
    cur.close()
    return msg

  def exec_op(self, op, receiver, sender=None):
    cur = self.conn.cursor()
    s_id = Client.get_client_id(sender)
    r_id = receiver.client_id
    q_id = Queue.get_queue_id(self)
    cur.execute("SELECT * FROM {0}(%s, %s, %s)".format(op), (r_id, q_id, s_id))
    res = cur.fetchone()
    cur.close()
    return res

  def pop(self, receiver, sender=None):
    return self.exec_op("pop", receiver, sender)
  
  def peek(self, receiver, sender=None):
    return self.exec_op("peek", receiver, sender)

  def remove(self):
    cur = self.conn.cursor()
    cur.execute("SELECT * FROM remove_queue(%s)", (self.queue_id, ))
    res = cur.fetchone()[0]
    cur.close()
    return res 

  def get_queue_id(self):
    if self is None:
      return 0
    return self.queue_id
