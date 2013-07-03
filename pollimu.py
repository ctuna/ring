#!/usr/bin/python

import time, sys
import lib.motetalk as motetalk
from lib.motetalk import cmd, packetify, setpwm

def startup(m):
  m.sendbase(cmd.radio(25))
  m.sendbase(cmd.flags(cmd.ledmode_cnt + cmd.notick))

  # m.sendheli(cmd.flags(cmd.ledmode_cnt + cmd.tick))

  m.sendbase(cmd.mode(cmd.mode_sniff))

def end(m):
  m.sendbase(cmd.mode(cmd.mode_spin))
  m.end()

def getimu(m, addr):
  m.setaddr(addr)
  m.flush()
  m.loadheli(cmd.mode(cmd.mode_get_imu))
  m.sendbase(cmd.mode(cmd.mode_sendrecv))
  try:
    (arr, t, crc) = m.nextline()
    if (arr == False):
      errwrite("\n** Error ** ")
      errwrite(repr(t) + "\n\n")
      return -1, None
    elif arr:
      if crc:
        errwrite("o")
        return 1, None
      else:
        return 0, arr
    else:
      errwrite("x")
      return 1, None
  except:
    errwrite(repr(sys.exc_info()))
    errwrite("\nQuitting... \n")
    return -1, None

def errwrite(s):
  #sys.stderr.write(s)
  #sys.stderr.flush()
  return

class motepoll:
  num_good = 0
  num_bad = 0
  num_skip = 0

  done = 0
  n = 0
  oldarr = []

  header =    "addr len cmd type n sx sy z1 z3 ta mx my mz lx ly lz ti gx gy gz cm ct ca ce cp mychk chk lqi rssi"
  fmtstr = '!  H    b   b   b    H H  H  H  H  H  h  h  h  H  H  H  H  h  h  h  h  h  h  h  h  B     H   B   B'

  def __init__(self):
    self.m = motetalk.motetalk(self.fmtstr, self.header, "COM4", debug=False,timeout=0.5)
    startup(self.m)

    errwrite( "Sniffing...\n")
    #print "ts " + header

    try:
      (arr, t, crc) = self.m.nextline()
      (arr, t, crc) = self.m.nextline()
      (arr, t, crc) = self.m.nextline()
    except: 
      pass

  def get(self, addr):
    ret, arr = getimu(self.m, addr)
    if (ret == 0):
      if (arr['lx'] > 36000): return 'l'
      if (arr['lx'] < 32000): return 'r'
      if (arr['ly'] > 36000): return 'u'
      if (arr['ly'] < 32000): return 'd'
    return "x"
