import time

class Timer:
	def __init__(self):
		self.last_time = time.time()
		self.Elapsed = 0
	def elapsed(self, interval, ms = True):
		current_time = time.time()
		new_time = (current_time - self.last_time) * 1000 if ms else (current_time - self.last_time)
		if new_time >= interval:
			self.last_time = current_time
			self.Elapsed = new_time
			return True
		return False

	def restart(self):
		self.last_time = time.time()
