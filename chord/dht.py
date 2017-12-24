from chord.chord import Local, Daemon, repeat_and_sleep, inrange
from chord.remote import Remote
from chord.address import Address
import json
import hashlib

# data structure that represents a distributed hash table
class DHT(object):
  def __init__(self, local_address, remote_address = None):
    self.local_ = Local(local_address, remote_address)
    def set_wrap(msg):
      return self._set(msg)
    def get_wrap(msg):
      return self._get(msg)

    self.data_ = {}
    self.shutdown_ = False

    self.local_.register_command("set", set_wrap)
    self.local_.register_command("get", get_wrap)

    self.daemons_ = {}
    self.daemons_['distribute_data'] = Daemon(self, 'distribute_data')
    self.daemons_['distribute_data'].start()

    self.local_.start()

  def shutdown(self):
    print("shutdown dht node")
    self.local_.shutdown()
    self.shutdown_ = True

  def _get(self, request):
    try:
      data = json.loads(request)
      # we have the key
      return json.dumps({'status':'ok', 'data':self.get(data['key'])})
    except Exception:
      # key not present
      return json.dumps({'status':'failed'})

  def _set(self, request):
    try:
      data = json.loads(request)
      key = data['key']
      value = data['value']
      self.set(key, value)
      return json.dumps({'status':'ok'})
    except Exception:
      # something is not working
      return json.dumps({'status':'failed'})

  def get(self, key):
    try:
      return self.data_[key]
    except Exception:
      # not in our range
      suc = self.local_.find_successor(int(hashlib.sha256(str(key).encode("utf-8")).hexdigest(),16))
      if self.local_.id() == suc.id():
        # it's us but we don't have it
        return None
      try:
        response = suc.command('get %s' % json.dumps({'key':key}))
        if not response:
          raise Exception
        value = json.loads(response)
        if value['status'] != 'ok':
          raise Exception
        return value['data']
      except Exception:
        return None
  def set(self, key, value):
    # eventually it will distribute the keys
    self.data_[key] = value

  @repeat_and_sleep(5)
  def distribute_data(self):
    if self.shutdown_:
        return False
    else:
      to_remove = []
      # to prevent from RTE in case data gets updated by other thread
      keys = list(self.data_.keys())
      for key in keys:
        if self.local_.predecessor() and \
           not inrange(int(hashlib.sha256(str(key).encode("utf-8")).hexdigest(),16), self.local_.predecessor().id(1), self.local_.id(1)):
          print(int(hashlib.sha256(str(key).encode("utf-8")).hexdigest(),16))
          try:
            node = self.local_.find_successor(int(hashlib.sha256(str(key).encode("utf-8")).hexdigest(),16))
            node.command("set %s" % json.dumps({'key':key, 'value':self.data_[key]}))
            # print "moved %s into %s" % (key, node.id())
            to_remove.append(key)
            print("migrated")
          except OSError:
            print("error migrating")
            # we'll migrate it next time
            pass
      # remove all the keys we do not own any more
      for key in to_remove:
        del self.data_[key]
      # Keep calling us
      return True

def create_dht(lport):
  laddress = [Address('127.0.0.1', port) for port in lport]
  r = [DHT(laddress[0])]
  for address in laddress[1:]:
    r.append(DHT(address, laddress[0]))
  return r


if __name__ == "__main__":
  import sys
  if len(sys.argv) == 2:
    dht = DHT(Address("127.0.0.1", sys.argv[1]))
  else:
    dht = DHT(Address("127.0.0.1", sys.argv[1]), Address("127.0.0.1", sys.argv[2]))
  input("Press any key to shutdown")
  print("shuting down..")
  dht.shutdown()

