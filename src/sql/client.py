
class Client(object):
  def __init__(self, conn):
    self.cur = conn.cursor()
    self.cur.execute("SELECT * FROM register_client()")
    self.client_id = self.cur.fetchone()[0]

  def queue_message(queue, content=None, receiver=None):
    return queue.queue_message(content, self.client_id, receiver)

  def dequeue_message(queue=None):
    pass
