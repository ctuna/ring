#/usr/bin/python

import time, sys
import lib.motetalk as motetalk
import serial, glob
from lib.motetalk import cmd, packetify, setpwm

# delta t, 1 second, 300 samples
delta_t = 1/300


def startup(m):
  m.sendbase(cmd.radio(23))
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

# we know for mac it will show as /dev/usb.tty*, so list all of them and ask user to choose
availables = glob.glob('/dev/tty.usb*')

print "All available ports:" 
index = 1
for port in availables:
	print '  ', index, port
	index += 1

try:
	num = int(raw_input('Enter the number:'))
	if num > 0 and num <= len(availables):
		selected = availables[num-1]
except Exception as e:
	print "invalid input!"
	exit(1)

header = "addr len cmd type n sx sy z1 z3 ta lx ly lz ti gx gy gz mx my mz Address"
fmtstr = "! H  b   b   b  H  H  H  H  H  H  H  H  H  H  h  h  h h h h H"

m = motetalk.motetalk(fmtstr, header, selected, debug=False)
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

while True:
  try:
    (arr, t, crc) = m.nextline()
    if (arr == False):
      sys.stderr.write("\n** Error ** ")
      sys.stderr.write(repr(t) + "\n\n")
      break
    elif arr:
      if crc:
        sys.stderr.write("o")
        sys.stderr.flush()
      else:
        s = repr(m)
        split = s.split(" ")
        print m
    else:
      sys.stderr.write("x")
      sys.stderr.flush()
  except:
    sys.stderr.write(repr(sys.exc_info()))
    sys.stderr.write("\nQuitting... \n")
    done = 1

end(m)
