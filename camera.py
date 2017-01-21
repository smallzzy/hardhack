import numpy as np
import cv2
import time
import io
import threading

class Camera(threading.Thread):
	thread = None  # background thread that reads frames from camera
	frame = None  # current frame is stored here by background thread
	last_access = 0  # time of last client access to the camera

	def initialize(self):
		if Camera.thread is None:
			# start background frame thread
			Camera.thread = threading.Thread(target=self.worker)
			Camera.thread.start()

			# wait until frames start to be available
			while self.frame is None:
				time.sleep(0)

	def get_frame(self):
		current_time = time.time()
		#if
		Camera.last_access = time.time()
		self.initialize()
		return self.frame

	def __del__(self):
		cap.release()
		self.thread = None

	@classmethod
	def worker(self):
		cap = cv2.VideoCapture(0)

		while cap.isOpened() is False:
			cap.open()

		while(cap.isOpened()):
			ret, frame = cap.read()
		
			if ret is True:
				# Our operations on the frame come here
				ret2, jpeg = cv2.imencode('.jpg', frame)

				self.frame = jpeg.tobytes()

				#self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

			if time.time() - self.last_access > 10:# no access time out
				break
		cap.release()
		self.thread = None
