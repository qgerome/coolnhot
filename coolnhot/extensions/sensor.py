# -*- coding: UTF-8 -*-

__author__ = 'quentingerome'
__all__ = ['Sensor']


class FakeSensor(object):
	def __init__(self):
		super(FakeSensor, self).__init__()

	def get_temp(self):
		return 0

	def get_rel_humidity(self):
		return 0


class Sensor(object):
	def __init__(self, app=None):
		super(Sensor, self).__init__()
		self._impl = None
		if app is not None:
			self.init_app(app)

	def init_app(self, app):
		if app.config.get('SENSOR_DEBUG'):
			self._impl = FakeSensor()
		else:
			from .. import si7020
			self._impl = si7020.Si7020()

	def get_temp(self):
		if not self._impl:
			raise Exception("App not initialized")

		return self._impl.get_temp()

	def get_rel_humidity(self):
		if not self._impl:
			raise Exception("App not initialized")

		return self._impl.get_rel_humidity()