from datetime import datetime

class Log():

	DEBUG = 1
	INFO = 2

	LOG_LEVEL = DEBUG

	@staticmethod
	def i(x):

		if (Log.LOG_LEVEL < Log.INFO):
			return;

		timestamp = datetime.utcnow().strftime('%m-%d %H:%M:%S.%f')[:-3]

		print ("%s\tI/%s") % (timestamp, x)
		
		return;

	@staticmethod
	def d(x):

		if (Log.LOG_LEVEL < Log.DEBUG):
			return;

		timestamp = datetime.utcnow().strftime('%m-%d %H:%M:%S.%f')[:-3]

		print ("%s\tD/%s") % (timestamp, x)
		
		return;