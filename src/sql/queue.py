
import time

class Queue(object):
  def __init__(self, conn, queue_id=None):
    if queue_id is None:
      self.cur = conn.cursor()
      self.cur.execute("SELECT * FROM create_queue()")
      self.queue_id = self.cur.fetchone()[0]
    else:
      self.queue_id = queue_id

  def send_message(content=None, sender, receiver=None):
    if receiver is None:
      r_id = 0
    else:
      r_id = receiver.client_id
    s_id = sender.client_id
    if content is None:
      content = "{0}".format(time.time())
    self.cur.execute("""SELECT * FROM send_message( 
      %s, %s, %s, %s)""", (self.queue_id, s_id, r_id, content)
    return self.cur.fetchone()

  def exec_op(op, receiver, sender=None):
    if sender is None:
      s_id = 0
    r_id = receiver.client_id
    self.cur.execute("SELECT * FROM {0}(%s, %s, %s)".format(op), (r_id, self.queue_id, s_id))
    return self.cur.fetchone()

  def pop(receiver, sender=None):
    return self.exec_op("pop", receiver, sender)
  
  def peek(receiver, sender=None):
    return self.exec_op("peek", receiver, sender)

  def remove():
    self.cur.execute("SELECT * FROM remove_queue(%s)", (self.queue_id, ))
    return self.cur.fetchone()[0]

