# -*- coding: UTF-8 -*-

__author__ = 'quentingerome'

import logging
from . import CoolnHotAppTestCase
from coolnhot.models import Measurement
from datetime import datetime
from dateutil.relativedelta import relativedelta

log = logging.getLogger(__name__)


class MeasurementTestCase(CoolnHotAppTestCase):
	def _create_fixtures(self):
		super(MeasurementTestCase, self)._create_fixtures()

	def test_create(self):
		from coolnhot.models import Measurement

		reading = Measurement(temperature=22.5, humidity=45.6)
		self.session.add(reading)
		self.session.commit()
		self.assertTrue(Measurement.query.count() == 1)

		self.session.delete(Measurement.query.first())
		self.session.commit()
		self.assertTrue(Measurement.query.count() == 0)

	def test_avg(self):
		now = datetime.utcnow()
		measurements = [
			Measurement(5.5, 43, created_at=now),
			Measurement(6.4, 45, created_at=now - relativedelta(minutes=5)),
			Measurement(7, 50, created_at=now - relativedelta(minutes=10)),
		]

		map(self.session.add, measurements)
		self.session.commit()

		avg = Measurement.query.avg(now - relativedelta(minutes=11), now + relativedelta(seconds=5))
		self.assertEquals(avg, (6.3, 46))