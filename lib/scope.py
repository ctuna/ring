#!/usr/bin/python

from pylab import ion, plot, draw, ioff, close
import threading, time

class scope (threading.Thread):
	p = []
	done = 0

	def __init__(self, numt=100, miny=0, maxy=4096, numy=1, delay=0):
		ion() 
		self.x = range(numt)
		self.y = [[miny for j in self.x] for i in range(numy)]
		self.y[0][0] = maxy
		for i in range(numy):
			line, = plot(self.x, self.y[i])
			self.p.append(line)
		self.delay = delay
		threading.Thread.__init__(self)

	def run(self):
		while not self.done:
			draw()
			if self.delay:
				time.sleep(self.delay)
		ioff()
		close()

	def end(self):
		self.done = 1

	def newy(self, *v):
		if len(v) == len(self.y):
			for i in range(len(self.y)):
				self.y[i].pop(0) 
				self.y[i].append(v[i])
				self.p[i].set_ydata(self.y[i])
