import sys

class linkstat:
  SUCCESS = 0
  ERR_COMM = -1
  ERR_CRC = -2
  ERR_SHORT = -3
  ERR_ADDR = -4
  ERR_CHKSUM = -5

  printing = 1

  num_good = 0
  num_bad = 0
  num_skip = 0

  addrrange = None
  addr = ""

  ginapkt = False

  nrange = None
  n = None

  lastpkt = None

  def reset(self):
    self.num_good = 0
    self.num_bad = 0
    self.num_skip = 0

    self.addrrange = None
    self.addr = ""

    self.ginapkt = False

    self.nrange = None
    self.n = None

    self.lastpkt = None

  def write(self, s):
    if self.printing:
      sys.stderr.write(s)
      sys.stderr.flush()

  def setaddr(self, rng, addr):
    self.addrrange = rng
    self.addr = addr

  def setgina(self):
    self.ginapkt = True

  def setcount(self, rng):
    self.nrange = rng

  def check(self, arr, crc):
    if (arr == False):
      self.write("\n** Error ** ")
      return self.ERR_COMM

    if arr and crc:
      self.write("o")
      self.num_bad = self.num_bad + 1
      return self.ERR_CRC

    elif arr:

      if (self.addrrange):
        if ("".join(arr[x] for x in self.addrrange) != self.addr):
          return self.ERR_ADDR
        arr = "".join([arr[x] for x in range(len(arr)) if x not in self.addrrange])

      if (self.ginapkt):
        pkt = map(ord, arr)
        length = pkt[0]
        if len(pkt) < length + 2:
          return self.ERR_SHORT
        checksum = ~sum(pkt[1:length+1]) & 0xff
        if pkt[length+1] != checksum:
          return self.ERR_CHKSUM
        arr = arr[1:length+1]
      
      self.lastpkt = arr

      if (self.nrange):
        n = 0
        for i in self.nrange:
          n = (n << 8) + ord(arr[i])
        dn = 1

        if self.n != None:
          maxn = 2**(8*len(self.nrange))
          dn = (n - self.n + maxn/2) % maxn - maxn/2
        if dn == 1: 
          self.write(".")
        else:
          self.write("!%d!" % (dn - 1))
          self.num_skip = self.num_skip + dn - 1
        self.n = n

      self.num_good = self.num_good + 1
      return self.SUCCESS

    else:
      self.write("x")
      self.num_bad = self.num_bad + 1
      return self.ERR_SHORT

  def toString(self):
    return self.__str__()
  def __repr__(self):
    return self.__str__()
  def __str__(self):
    ret = "%d Successful packets recieved\n" % self.num_good
    ret += "%d packet errors\n" % self.num_bad
    ret += "%d skipped packets\n" % self.num_skip
    if (self.num_skip + self.num_good):
      ret += "%4.2f%% packet drop rate\n" % (self.num_skip*100.0 / (self.num_skip+self.num_good))
    return ret

