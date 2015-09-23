
class Client(object):
  def __init__(self, conn):
    self.cur = conn.cursor()
    self.cur.execute("SELECT * FROM register_client()")
    self.client_id = self.cur.fetchone()[0]

  def send_message(queue, content=None, receiver=None):
    return queue.send_message(content, self, receiver)

  def pop(queue, sender=None):
    return queue.pop(self, sender)
  
  def peek():
    return queue.peek(self, sender)

  def remove():
    self.cur.execute("SELECT * FROM remove_client(%s)", (self.client_id, ))
    return self.cur.fetchone()[0]
