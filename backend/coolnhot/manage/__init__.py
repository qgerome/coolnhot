# -*- coding: UTF-8 -*-

from flask.ext.script import Command
from ..extensions import sensor, db
from ..models import Measurement
import logging

log = logging.getLogger(__name__)


class MeasureCommand(Command):
	def run(self):
		log.info("Measuring temperature & relative humidity from sensor...")
		temp, rel_humidity = sensor.get_temp(), sensor.get_rel_humidity()
		measurement = Measurement(temp, rel_humidity)
		db.session.add(measurement)
		db.session.commit()
		log.info("Measurement done: %r", measurement)