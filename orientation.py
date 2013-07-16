#/usr/bin/python

import time, sys
import lib.motetalk as motetalk
import serial, glob
import OSC
from lib.motetalk import cmd, packetify, setpwm

# delta t, 1 second, 300 samples
delta_t = 1.0/300
angle = 0
# complimentary filter tutorial:
# http://web.mit.edu/scolton/www/filter.pdf
# angle = (0.98)*(angle + gyro * dt) + (0.02)*(x_acc);


def osc_send(addr, data):
  msg = OSC.OSCMessage() #  we reuse the same variable msg used above overwriting it
  msg.setAddress(addr)
  msg.append(data)
  client.send(msg) # now we dont need to tell the client the address anymore

  
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

sys.stderr.write( "Starting up OSC...\n")
client = OSC.OSCClient()
client.connect( ('127.0.0.1', 8000) ) # note that the argument is a tupple and not two arguments


sys.stderr.write( "Sniffing...\n")
print "ts " + header

try:
  (arr, t, crc) = m.nextline()
  (arr, t, crc) = m.nextline()
  (arr, t, crc) = m.nextline()
except: 
  sys.stderr.write("oops")
  pass

gyro_integral = 0
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

        # magic number 8.2 was calibrated by integration for 360 degress
        x_gyro = float(arr['gx']) / 8.2 / 57.2
        gyro_integral = gyro_integral + x_gyro * delta_t

        # 2000 as base, 1220 as -1g, 
        x_acc = (float(arr['sx']) - 2000) / 780
        angle = (0.98) * (angle + x_gyro * delta_t) + (0.02) * (x_acc);
        print x_gyro, angle * 57.2 

        # osc_send("/gyro/x", x_gyro)
        # osc_send("/acc/x", x_acc)
        osc_send("/angle", angle * 57.2 / 360)
        # osc_send("/gyro_integral", gyro_integral)

    else:
      sys.stderr.write("x")
      sys.stderr.flush()
  except:
    sys.stderr.write(repr(sys.exc_info()))
    sys.stderr.write("\nQuitting... \n")
    done = 1

end(m)
