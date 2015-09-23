
import time

class Queue(object):
  def __init__(self, conn, queue_id=None):
    if queue_id is None:
      self.cur = conn.cursor()
      self.cur.execute("SELECT * FROM create_queue()")
      self.queue_id = self.cur.fetchone()[0]
    else:
      self.queue_id = queue_id

  def queue_message(content=None, sender, receiver=None):
    if receiver is None:
      receiver = 0
    if content is None:
      content = "{0}".format(time.time())
    self.cur.execute("""SELECT * FROM send_message( 
      %s, %s, %s, %s)""", (self.queue_id, sender, receiver, content)
    return self.cur.fetchone()
