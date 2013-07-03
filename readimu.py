#/usr/bin/python

import time, sys
import lib.motetalk as motetalk
from lib.motetalk import cmd, packetify, setpwm

def startup(m):
  m.sendbase(cmd.radio(25))
  # time.sleep(1)
  m.sendbase(cmd.flags(cmd.ledmode_cnt + cmd.notick))
  # time.sleep(1)

  m.sendheli(cmd.flags(cmd.ledmode_cnt + cmd.tick))
  # time.sleep(1)
  m.sendheli(cmd.mode(cmd.mode_imu_loop))
  # time.sleep(1)

  m.sendbase(cmd.mode(cmd.mode_sniff))
  # time.sleep(1)

def end(m):
  m.sendbase(cmd.mode(cmd.mode_spin))
  m.end()

num_good = 0
num_bad = 0
num_skip = 0

done = 0
n = 0
oldarr = []

#header =    "addr len cmd type n sx sy z1 z3 ta mx my mz lx ly lz ti gx gy gz mychk chk lqi rssi"
#fmtstr = '!  H    b   b   b    H H  H  H  H  H  h  h  h  H  H  H  H  h  h  h  B     H   B   B'
# header =    "addr len cmd type n mx my mz lx ly lz ti gx gy gz cm ct ca ce cp i0 i1 i2 i3 i4 i5 i6 i7 i8 i9 ia ib ic mychk chk lqi rssi"
# fmtstr = '!  H    b   b   b    H h  h  h  H  H  H  H  h  h  h  H  H  H  H  H  B  B  B  B  B  B  B  B  B  B  B  B  B  B     H   B   B'
#header =    "addr len cmd type n sx sy z1 z3 ta mx my mz lx ly lz ti gx gy gz cm ct ca ce cp mychk chk lqi rssi"
#fmtstr = '!  H    b   b   b    H H  H  H  H  H  h  h  h  H  H  H  H  h  h  h  h  h  h  h  h  B     H   B   B'
header =    "addr len cmd type n sx sy z1 z3 ta mx my mz lx ly lz ti gx gy gz cm ct ca ce cp mychk chk lqi rssi"
fmtstr = '!  H    b   b   b    H H  H  H  H  H  h  h  h  H  H  H  H  h  h  h  h  h  h  h  h  B     H   B   B'



m = motetalk.motetalk(fmtstr, header, "/dev/tty.usbmodem1421", debug=False)
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

while not done:
  try:
    (arr, t, crc) = m.nextline()
    if (arr == False):
      done = 1
      sys.stderr.write("\n** Error ** ")
      sys.stderr.write(repr(t) + "\n\n")
    elif arr:
      if crc:
        sys.stderr.write("o")
        sys.stderr.flush()
        num_bad = num_bad + 1
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
    else:
      sys.stderr.write("x")
      sys.stderr.flush()
      num_bad = num_bad + 1
  except:
    sys.stderr.write(repr(sys.exc_info()))
    sys.stderr.write("\nQuitting... \n")
    done = 1

end(m)
sys.stderr.write( "%d Successful packets recieved\n" % num_good)
sys.stderr.write( "%d packet errors\n" % num_bad)
sys.stderr.write( "%d skipped packets\n" % num_skip)
if (num_skip + num_good):
  sys.stderr.write( "%4.2f%% packet drop rate\n" % (num_skip * 100.0 / (num_skip + num_good)))

