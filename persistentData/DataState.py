import enum
import sys
import threading
import time
import os
import json

class UpdateListener(object):
	def update(self):
		raise NotImplementedError();

class StateUpdateThread(threading.Thread):
	active = None
	
	def __init__(self, dataObj, interval):
		self.active = True
		threading.Thread.__init__(self)
		self.dataObj = dataObj
		self.interval = interval
		self.start()
	
	def run(self):
		while(self.active):
			self.dataObj.update();
			time.sleep(self.interval / 1000)
	
	def stop(self):
		if (not self.active or not self.is_alive()):
			raise RuntimeError("State Thread encountered fatal error while shutting down. Already shut down.")
		self.active = False;
		self.join();
		self.dataObj = None;

class GlobalState(UpdateListener):
	
	"""State enum of the Persistent Data."""
	"""State Graph in :ref:`Graph image <doc/persistentStateGraph.png>`"""
	class __PersistanceState(enum.IntFlag):
		READY_BIT			= 1												#Default state after initialization. All data is persistently stored and the buffer is synced up.
		BUFFER_BEHIND_BIT	= 2												#Entry state. The data in persistent storage is ahead of the buffer state. Should normally only happen on loadup or when the file is modified.
		BUFFER_AHEAD_BIT	= 4												#Data in the buffer has been modified. Persistent data needs to be updated *soon*.
		IN_OUT_BIT			= 8												#Buffer is currently syncing.
		
		BUFFER_AHEAD		= READY_BIT | BUFFER_AHEAD_BIT					#Valid dirty buffer state
		BUFFER_BEHIND		= READY_BIT | BUFFER_BEHIND_BIT					#Valid outdated buffer state
		READY				= READY_BIT										#(Possibly Redundant) Buffer valid and synced. Default State.
		READING				= READY | IN_OUT_BIT | BUFFER_BEHIND			#The buffer is being updated from the persistent storage.
		WRITING				= READY | IN_OUT_BIT | BUFFER_AHEAD				#The buffer is being stored to the persistent storage.
		
		GENERIC_ERROR		= 0												#Generic invalid state. System needs to be either reinitialized or forced into a synchronized state by reloading from disk.
		FATAL_ERROR			= GENERIC_ERROR | BUFFER_AHEAD | BUFFER_BEHIND	#Fatal data corruption. System needs to be reinitialized.
		IO_ERROR			= GENERIC_ERROR | IN_OUT_BIT					#Error while writing or reading the buffer. Data loss inevitable. must be reinitialized.
		
		def update_transfer(self):
			if (self == self.READING or self == self.WRITING):
				self = self.READY
				return True
			elif (self == self.READY):
				self = self.GENERIC_ERROR
				return False
			elif (self & self.READY_BIT == 0):
				return False
			else:
				return True
		
		def force_read_transfer(self):
			if (self == self.GENERIC_ERROR):
				self = self.BUFFER_BEHIND
				return True
			elif (self == self.BUFFER_AHEAD):
				self = self.READING
				return True
			#else:
				#return read_transfer();
				
		def force_write_transfer(self):
			if (self == self.BUFFER_BEHIND):
				self = self.WRITING
				return True
			#else:
				#return write_transfer();
	
		def is_valid(self):
			return self & self.READY_BIT
		def is_ready(self):
			return self == self.BUFFER_AHEAD or self == self.READY
		
		def __str__(self):
			return self.name
	
	__instance = None
	
	
	""" Static access method. """
	@staticmethod 
	def getInstance():
		if GlobalState.__instance == None:
			GlobalState()
		return GlobalState.__instance
	
	""" Static stestruction Method """
	@staticmethod
	def destroyInstance():
		if GlobalState.__instance == None:
			raise RuntimeError("No instance available.")
		else:
			GlobalState.__instance.__stateUpdateThread.stop()
			GlobalState.__instance = None
	
	""" Virtually private constructor. """
	def __init__(self):
		self.__persistenceState = GlobalState.__PersistanceState.BUFFER_BEHIND
		self.__state = {}
		self.__stateUpdateThread = StateUpdateThread( self, 1000)
		
		if GlobalState.__instance != None:
			raise Exception("Attempted to construct the singleton explicitly. Use getInstance() instead.")
		else:
			GlobalState.__instance = self
		
		
	def __save(self):
		print("saving state...")
		with open( "state.json", "w+") as f:
			json.dump(self.__state, f)
		
	def __load(self):
		if (not os.path.exists("state.json")):
			return
		print("loading state...")
		with open( "state.json", "r") as f:
			self.__state = json.load(f)
	
	def flush(self):
		self.update()
	
	def update(self):
		if (self.__persistenceState == GlobalState.__PersistanceState.BUFFER_BEHIND):
			if (self.__persistenceState == GlobalState.__PersistanceState.BUFFER_BEHIND):
				self.__persistenceState = GlobalState.__PersistanceState.READING;
			elif (self.__persistenceState == GlobalState.__PersistanceState.BUFFER_AHEAD):
				self.__persistenceState = GlobalState.__PersistanceState.GENERIC_ERROR
				raise RuntimeError("Encountered Generic Error")
			elif (self.__persistenceState == GlobalState.__PersistanceState.WRITING):
				self.__persistenceState = GlobalState.__PersistanceState.IO_ERROR
				raise RuntimeError("Encountered IO Error")
			elif (self.__persistenceState & GlobalState.__PersistanceState.READY_BIT == 0):
				raise RuntimeError("Encountered Generic Error")
				
			self.__load()
			
			if (self.__persistenceState == GlobalState.__PersistanceState.READING or self.__persistenceState == GlobalState.__PersistanceState.WRITING):
				self.__persistenceState = GlobalState.__PersistanceState.READY
			elif (self.__persistenceState == GlobalState.__PersistanceState.READY):
				self.__persistenceState = GlobalState.__PersistanceState.GENERIC_ERROR
				raise RuntimeError("Encountered Generic Error")
			elif (self.__persistenceState & GlobalState.__PersistanceState.READY_BIT == 0):
				raise RuntimeError("Encountered Generic Error")
		elif (self.__persistenceState == GlobalState.__PersistanceState.BUFFER_AHEAD):
			if (self.__persistenceState == GlobalState.__PersistanceState.BUFFER_BEHIND):
				self.__persistenceState = GlobalState.__PersistanceState.GENERIC_ERROR
				raise RuntimeError("Encountered Generic Error")
			elif (self.__persistenceState == GlobalState.__PersistanceState.BUFFER_AHEAD):
				self.__persistenceState = GlobalState.__PersistanceState.WRITING
			elif (self.__persistenceState == GlobalState.__PersistanceState.READING):
				self.__persistenceState = GlobalState.__PersistanceState.IO_ERROR
				raise RuntimeError("Encountered IO Error")
			elif (self.__persistenceState & GlobalState.__PersistanceState.READY_BIT == 0):
				raise RuntimeError("Encountered Generic Error")
				
			self.__save()
			
			if (self.__persistenceState == GlobalState.__PersistanceState.READING or self.__persistenceState == GlobalState.__PersistanceState.WRITING):
				self.__persistenceState = GlobalState.__PersistanceState.READY
			elif (self.__persistenceState == GlobalState.__PersistanceState.READY):
				self.__persistenceState = GlobalState.__PersistanceState.GENERIC_ERROR
				raise RuntimeError("Encountered Generic Error")
			elif (self.__persistenceState & GlobalState.__PersistanceState.READY_BIT == 0):
				raise RuntimeError("Encountered Generic Error")
	
	def get(self, id, default):
		if (not id in self.__state.keys()):
			return default
		else:
			return self.__state[id]
	
	def set(self, id, value):
		if (self.__persistenceState == GlobalState.__PersistanceState.BUFFER_BEHIND):
			self.flush()
		elif (self.__persistenceState == GlobalState.__PersistanceState.READING or self.__persistenceState == GlobalState.__PersistanceState.WRITING):
			self.__persistenceState = GlobalState.__PersistanceState.IO_ERROR
			raise RuntimeError("Encountered IO Error")
		elif (self.__persistenceState == GlobalState.__PersistanceState.READY):
			self.__persistenceState = GlobalState.__PersistanceState.BUFFER_AHEAD
		elif (self.__persistenceState & GlobalState.__PersistanceState.READY_BIT == 0):
			raise RuntimeError("Encountered Generic Error")
		self.__state[id] = value;
	
	def is_ready(self):
		return self.__persistenceState.is_ready()
	
	def is_valid(self):
		return self.__persistenceState.is_valid()
	
	def get_state(self):
		return self.__persistenceState
	

if __name__ == '__main__':
	print("This is a library file for providing a thread safe persistent state. Like a lightweight database.")
	print("!! It will only test its own functionality. !!")
	print("Running Test...")
	instance = GlobalState.getInstance()
	
	if (id(instance) != id(GlobalState.getInstance())):
		print("!!!FATAL!!! Singleton not working properly.")
		sys.exit()
	
	GlobalState.destroyInstance();
