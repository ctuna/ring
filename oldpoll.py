#!/usr/bin/python

import time, sys
import lib.motetalk as motetalk
from lib.motetalk import cmd, packetify, setpwm

def startup(m):
  m.sendbase(cmd.radio(25))
  m.sendbase(cmd.flags(cmd.ledmode_cnt + cmd.notick))

  m.sendheli(cmd.flags(cmd.ledmode_cnt + cmd.tick))

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
      sys.stderr.write("\n** Error ** ")
      sys.stderr.write(repr(t) + "\n\n")
      return -1, None
    elif arr:
      if crc:
        sys.stderr.write("o")
        sys.stderr.flush()
        return 1, None
      else:
        return 0, arr
    else:
      sys.stderr.write("x")
      sys.stderr.flush()
      return 1, None
  except:
    sys.stderr.write(repr(sys.exc_info()))
    sys.stderr.write("\nQuitting... \n")
    return -1, None

num_good = 0
num_bad = 0
num_skip = 0

done = 0
n = 0
oldarr = []

header =    "addr len cmd type n sx sy z1 z3 ta mx my mz lx ly lz ti gx gy gz cm ct ca ce cp mychk chk lqi rssi"
fmtstr = '!  H    b   b   b    H H  H  H  H  H  h  h  h  H  H  H  H  h  h  h  h  h  h  h  h  B     H   B   B'

m = motetalk.motetalk(fmtstr, header, "/dev/ttyACM0", debug=False)
startup(m)

sys.stderr.write( "Sniffing...\n")
print "ts " + header

try:
  (arr, t, crc) = m.nextline()
  (arr, t, crc) = m.nextline()
  (arr, t, crc) = m.nextline()
except: 
  sys.stderr.write("oops")
  pass

decimator = 0
while not done:
  decimator += 1
  if (decimator % 3 == 0):
    print "2d"
    ret, arr = getimu(m, [0x00, 0x2d])
  else:
    print "cc"
    ret, arr = getimu(m, [0x00, 0xcc])

  if ret == -1:
    done = 1
  elif ret == 1:
    num_bad += 1
  else:
    if oldarr:
      dn = ((arr['n'] - n + 32768) % 65536) - 32768
      if dn == 1: 
        sys.stderr.write(".")
      else:
        sys.stderr.write("!%d!" % (dn - 1))
        num_skip = num_skip + dn - 1
      sys.stderr.flush()

    print repr(m)

    n = arr['n']
    oldarr = arr
    num_good = num_good + 1

  time.sleep(.2)

end(m)

sys.stderr.write( "%d Successful packets recieved\n" % num_good)
sys.stderr.write( "%d packet errors\n" % num_bad)
sys.stderr.write( "%d skipped packets\n" % num_skip)
if (num_skip + num_good):
  sys.stderr.write( "%4.2f%% packet drop rate\n" % (num_skip * 100.0 / (num_skip + num_good)))

