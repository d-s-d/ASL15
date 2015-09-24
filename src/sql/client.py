
class Client(object):
  def __init__(self, conn, name=None):
    self.cur = conn.cursor()
    if name is None:
      self.cur.execute("SELECT * FROM register_client(null)")
    else:
      self.cur.execute("SELECT * FROM register_client(%s)", name)
    self.client_id = self.cur.fetchone()[0]

  def send_message(self, queue, content=None, receiver=None):
    return queue.send_message(self, receiver, content)

  def pop(self, queue, sender=None):
    return queue.pop(self, sender)
  
  def peek(self, queue, sender=None):
    return queue.peek(self, sender)

  def remove(self):
    self.cur.execute("SELECT * FROM remove_client(%s)", (self.client_id, ))
    return self.cur.fetchone()[0]

  def get_client_id(self):
    if self is None:
      return 0
    return self.client_id
